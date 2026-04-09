from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid

from database import db, STRIPE_API_KEY, logger
from auth import require_dj
from france_geo import DEPARTMENTS_FRANCE

router = APIRouter()

ZONE_EXTENSION_PRICE = 20.00
MAX_DEPARTMENTS = 4


@router.get("/dj/zone-status")
async def get_zone_status(request: Request):
    """Get DJ's current zone configuration"""
    user_data = await require_dj(request)
    profile = await db.dj_profiles.find_one({"user_id": user_data["user_id"]})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouv\u00e9")
    departments_zones = profile.get("departments_zones", [])
    primary_dept = profile.get("department_code", "")
    zones_detail = []
    for dept_code in departments_zones:
        dept_info = DEPARTMENTS_FRANCE.get(dept_code, {})
        zones_detail.append({"code": dept_code, "name": dept_info.get("name", dept_code), "is_primary": dept_code == primary_dept})
    return {
        "primary_department": primary_dept,
        "primary_department_name": DEPARTMENTS_FRANCE.get(primary_dept, {}).get("name", ""),
        "departments_zones": departments_zones, "zones_detail": zones_detail,
        "total_departments": len(departments_zones), "max_departments": MAX_DEPARTMENTS,
        "extra_departments": max(0, len(departments_zones) - 1), "extension_price": ZONE_EXTENSION_PRICE,
    }


@router.get("/dj/available-departments")
async def get_available_departments(request: Request):
    """Get list of departments the DJ can add"""
    user_data = await require_dj(request)
    profile = await db.dj_profiles.find_one({"user_id": user_data["user_id"]})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouv\u00e9")
    current_zones = set(profile.get("departments_zones", []))
    all_depts = []
    for code, info in sorted(DEPARTMENTS_FRANCE.items(), key=lambda x: x[0]):
        all_depts.append({"code": code, "name": info["name"], "selected": code in current_zones})
    return all_depts


@router.post("/dj/zone/add-department")
async def add_department_zone(request: Request):
    """Add a department to DJ's zone (creates Stripe checkout for payment)"""
    user_data = await require_dj(request)
    body = await request.json()
    dept_code = body.get("department_code", "").strip()
    origin_url = body.get("origin_url", "")
    if not dept_code:
        raise HTTPException(status_code=400, detail="Code d\u00e9partement requis")
    if dept_code not in DEPARTMENTS_FRANCE:
        raise HTTPException(status_code=400, detail="D\u00e9partement non reconnu")
    profile = await db.dj_profiles.find_one({"user_id": user_data["user_id"]})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouv\u00e9")
    current_zones = profile.get("departments_zones", [])
    if dept_code in current_zones:
        raise HTTPException(status_code=400, detail="Ce d\u00e9partement est d\u00e9j\u00e0 dans votre zone")
    if len(current_zones) >= MAX_DEPARTMENTS:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_DEPARTMENTS} d\u00e9partements autoris\u00e9s")
    dept_name = DEPARTMENTS_FRANCE[dept_code]["name"]
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        success_url = f"{origin_url}/zone/success?dept={dept_code}"
        cancel_url = f"{origin_url}/zone/cancel"
        checkout_request = CheckoutSessionRequest(
            amount=ZONE_EXTENSION_PRICE, currency="eur",
            success_url=success_url, cancel_url=cancel_url,
            metadata={"user_id": user_data["user_id"], "type": "zone_extension",
                      "department_code": dept_code, "department_name": dept_name}
        )
        session = await stripe_checkout.create_checkout_session(checkout_request)
        await db.payment_transactions.insert_one({
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}", "session_id": session.session_id,
            "user_id": user_data["user_id"], "amount": ZONE_EXTENSION_PRICE, "currency": "eur",
            "type": "zone_extension", "department_code": dept_code, "department_name": dept_name,
            "status": "pending", "payment_status": "initiated", "created_at": datetime.now(timezone.utc)
        })
        return {"checkout_url": session.url, "session_id": session.session_id, "department": dept_name, "amount": ZONE_EXTENSION_PRICE}
    except Exception as e:
        logger.error(f"Zone extension checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur paiement: {str(e)}")


@router.delete("/dj/zone/remove-department/{dept_code}")
async def remove_department_zone(dept_code: str, request: Request):
    """Remove a department from DJ's zone (except primary)"""
    user_data = await require_dj(request)
    profile = await db.dj_profiles.find_one({"user_id": user_data["user_id"]})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouv\u00e9")
    if dept_code == profile.get("department_code"):
        raise HTTPException(status_code=400, detail="Impossible de retirer le d\u00e9partement principal")
    current_zones = profile.get("departments_zones", [])
    if dept_code not in current_zones:
        raise HTTPException(status_code=400, detail="Ce d\u00e9partement n'est pas dans votre zone")
    new_zones = [d for d in current_zones if d != dept_code]
    await db.dj_profiles.update_one({"user_id": user_data["user_id"]}, {"$set": {"departments_zones": new_zones}})
    return {"message": f"D\u00e9partement {dept_code} retir\u00e9", "departments_zones": new_zones}
