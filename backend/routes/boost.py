from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid

from database import db, STRIPE_API_KEY, logger
from auth import require_dj

router = APIRouter()

BOOST_PLANS = {
    "1_week": {"amount": 18.00, "days": 7, "label": "1 semaine", "description": "18\u20ac / 7 jours"},
    "2_weeks": {"amount": 34.00, "days": 14, "label": "2 semaines", "description": "34\u20ac / 14 jours"},
    "1_month": {"amount": 60.00, "days": 30, "label": "1 mois", "description": "60\u20ac / 30 jours"},
}


@router.get("/boost/plans")
async def get_boost_plans():
    """Get available boost plans"""
    return [
        {"id": "1_week", "amount": 18.00, "currency": "eur", "label": "1 semaine", "description": "18\u20ac", "days": 7},
        {"id": "2_weeks", "amount": 34.00, "currency": "eur", "label": "2 semaines", "description": "34\u20ac", "days": 14, "savings": "\u00c9conomie 2\u20ac"},
        {"id": "1_month", "amount": 60.00, "currency": "eur", "label": "1 mois", "description": "60\u20ac", "days": 30, "savings": "\u00c9conomie 12\u20ac"},
    ]


@router.get("/boost/status")
async def get_boost_status(request: Request):
    """Get current DJ boost status"""
    user_data = await require_dj(request)
    profile = await db.dj_profiles.find_one({"user_id": user_data["user_id"]})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouv\u00e9")
    boost_active = profile.get("boost_active", False)
    boost_end = profile.get("boost_end")
    if boost_active and boost_end and boost_end < datetime.now(timezone.utc):
        await db.dj_profiles.update_one({"user_id": user_data["user_id"]}, {"$set": {"boost_active": False}})
        boost_active = False
    return {
        "boost_active": boost_active, "boost_plan": profile.get("boost_plan"),
        "boost_start": profile.get("boost_start"), "boost_end": boost_end,
        "days_remaining": max(0, (boost_end - datetime.now(timezone.utc)).days) if boost_active and boost_end else 0,
    }


@router.post("/boost/create-checkout")
async def create_boost_checkout(request: Request):
    """Create a Stripe checkout session for DJ boost"""
    user_data = await require_dj(request)
    body = await request.json()
    origin_url = body.get("origin_url", "")
    plan = body.get("plan", "1_week")
    if not origin_url:
        raise HTTPException(status_code=400, detail="origin_url requis")
    if plan not in BOOST_PLANS:
        raise HTTPException(status_code=400, detail="Plan de boost invalide")
    plan_details = BOOST_PLANS[plan]
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        success_url = f"{origin_url}/boost/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/boost/cancel"
        checkout_request = CheckoutSessionRequest(
            amount=plan_details["amount"], currency="eur",
            success_url=success_url, cancel_url=cancel_url,
            metadata={"user_id": user_data["user_id"], "type": "dj_boost",
                      "plan": plan, "days": str(plan_details["days"])}
        )
        session = await stripe_checkout.create_checkout_session(checkout_request)
        await db.payment_transactions.insert_one({
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}", "session_id": session.session_id,
            "user_id": user_data["user_id"], "amount": plan_details["amount"], "currency": "eur",
            "type": "boost", "plan": plan, "days": plan_details["days"],
            "status": "pending", "payment_status": "initiated", "created_at": datetime.now(timezone.utc)
        })
        return {"checkout_url": session.url, "session_id": session.session_id, "plan": plan, "amount": plan_details["amount"]}
    except Exception as e:
        logger.error(f"Boost checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur paiement: {str(e)}")
