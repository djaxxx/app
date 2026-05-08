from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
import uuid

from database import db
from auth import require_admin
from utils import convert_images_to_files
from france_geo import get_department_for_city

router = APIRouter()


@router.get("/admin/djs")
async def admin_list_djs(request: Request, page: int = 1, limit: int = 50):
    """Admin: List ALL DJs (including inactive/unpaid)"""
    await require_admin(request)
    skip = (page - 1) * limit
    total = await db.dj_profiles.count_documents({})
    djs = await db.dj_profiles.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).to_list(limit)
    return {"djs": djs, "total": total, "page": page, "limit": limit, "pages": (total + limit - 1) // limit}


@router.get("/admin/stats")
async def admin_stats(request: Request):
    """Admin: Get platform statistics"""
    await require_admin(request)
    total_djs = await db.dj_profiles.count_documents({})
    active_djs = await db.dj_profiles.count_documents({"is_active": True, "subscription_status": {"$in": ["active", "trial"]}})
    trial_djs = await db.dj_profiles.count_documents({"subscription_status": "trial"})
    expired_djs = await db.dj_profiles.count_documents({"subscription_status": {"$in": ["expired", "inactive"]}})
    boosted_djs = await db.dj_profiles.count_documents({"boost_active": {"$ne": False, "$exists": True}})
    total_contacts = await db.contact_requests.count_documents({})
    total_users = await db.users.count_documents({})
    return {
        "total_djs": total_djs, "active_djs": active_djs,
        "trial_djs": trial_djs, "expired_djs": expired_djs,
        "boosted_djs": boosted_djs, "total_contacts": total_contacts,
        "total_users": total_users,
    }


@router.get("/admin/contact-requests")
async def admin_contact_requests(request: Request, page: int = 1, limit: int = 50):
    """Admin: List all contact requests from clients to DJs"""
    await require_admin(request)
    skip = (page - 1) * limit
    total = await db.contact_requests.count_documents({})
    requests_list = await db.contact_requests.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).to_list(limit)
    # Batch fetch DJ names with $in instead of loop
    dj_user_ids = list({req.get("dj_user_id") for req in requests_list if req.get("dj_user_id")})
    dj_names = {}
    if dj_user_ids:
        djs = await db.dj_profiles.find(
            {"user_id": {"$in": dj_user_ids}}, {"user_id": 1, "nom_de_scene": 1, "_id": 0}
        ).to_list(len(dj_user_ids))
        dj_names = {dj["user_id"]: dj.get("nom_de_scene", "Inconnu") for dj in djs}
    for req in requests_list:
        req["dj_nom"] = dj_names.get(req.get("dj_user_id"), "Inconnu")
    return {"requests": requests_list, "total": total, "page": page, "limit": limit}


@router.post("/admin/create-dj")
async def admin_create_dj(request: Request):
    """Admin: Create a DJ profile with free active subscription"""
    await require_admin(request)
    body = await request.json()
    user_id = f"admin_dj_{uuid.uuid4().hex[:12]}"
    email = body.get("email", f"{user_id}@djmatch.fr")
    existing = await db.users.find_one({"email": email})
    if existing:
        user_id = existing["user_id"]
    else:
        await db.users.insert_one({
            "user_id": user_id, "email": email,
            "name": body.get("nom_de_scene", "DJ"), "picture": "",
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
        })
    existing_dj = await db.dj_profiles.find_one({"user_id": user_id})
    if existing_dj:
        raise HTTPException(status_code=400, detail="Ce DJ existe d\u00e9j\u00e0")
    city = body.get("ville", "")
    geo_data = {}
    if city:
        geo_result = get_department_for_city(city)
        if geo_result and "department_name" in geo_result:
            geo_data = geo_result
    now = datetime.now(timezone.utc)
    dj_data = {
        "user_id": user_id, "email": email,
        "nom": body.get("nom", ""), "prenom": body.get("prenom", ""),
        "nom_de_scene": body.get("nom_de_scene", ""),
        "telephone": body.get("telephone", ""), "siret": body.get("siret", ""),
        "siret_verified": True, "ville": city,
        "department_code": geo_data.get("department_code", body.get("department_code", "")),
        "department_name": geo_data.get("department_name", body.get("department_name", "")),
        "region_code": geo_data.get("region_code", body.get("region_code", "")),
        "region_name": geo_data.get("region_name", body.get("region_name", "")),
        "latitude": body.get("latitude"), "longitude": body.get("longitude"),
        "description": body.get("description", ""),
        "annees_experience": body.get("annees_experience", 0),
        "types_evenements": body.get("types_evenements", []),
        "materiel_son": body.get("materiel_son", ""),
        "materiel_lumiere": body.get("materiel_lumiere", ""),
        "tarif_indicatif": body.get("tarif_indicatif", "800"),
        "instagram": body.get("instagram", ""), "tiktok": body.get("tiktok", ""),
        "youtube": body.get("youtube", ""), "google_page": body.get("google_page", ""),
        "site_internet": body.get("site_internet", ""),
        "photo_profil": body.get("photo_profil", ""),
        "galerie_photos": body.get("galerie_photos", []),
        "subscription_status": "active", "subscription_plan": "admin_free",
        "subscription_end_date": (now + timedelta(days=36500)).isoformat(),
        "is_active": True, "is_verified": True, "badge_verifie": True,
        "nombre_vues": 0, "nombre_avis": 0, "note_moyenne": 0,
        "created_at": now, "updated_at": now, "added_by_admin": True,
    }
    convert_images_to_files(dj_data)
    await db.dj_profiles.insert_one(dj_data)
    del dj_data["_id"]
    return {"message": "DJ cr\u00e9\u00e9 avec succ\u00e8s (abonnement gratuit activ\u00e9)", "dj": dj_data}


@router.put("/admin/djs/{user_id}/toggle-subscription")
async def admin_toggle_subscription(user_id: str, request: Request):
    """Admin: Toggle DJ subscription status"""
    await require_admin(request)
    dj = await db.dj_profiles.find_one({"user_id": user_id})
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouv\u00e9")
    current_status = dj.get("subscription_status", "inactive")
    # Toggle: active/trial → inactive, inactive/expired → active
    if current_status in ("active", "trial"):
        new_status = "inactive"
    else:
        new_status = "active"
    update_data = {"subscription_status": new_status, "is_active": new_status == "active", "updated_at": datetime.now(timezone.utc)}
    if new_status == "active":
        update_data["subscription_plan"] = "admin_free"
        update_data["subscription_end_date"] = (datetime.now(timezone.utc) + timedelta(days=36500)).isoformat()
    await db.dj_profiles.update_one({"user_id": user_id}, {"$set": update_data})
    status_msg = "activé" if new_status == "active" else "désactivé"
    return {"message": f"DJ {status_msg} avec succès", "subscription_status": new_status}


@router.put("/admin/djs/{user_id}/toggle-boost")
async def admin_toggle_boost(user_id: str, request: Request):
    """Admin: Toggle DJ boost"""
    await require_admin(request)
    dj = await db.dj_profiles.find_one({"user_id": user_id})
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouv\u00e9")
    is_boosted = dj.get("boost_active", False)
    if is_boosted:
        await db.dj_profiles.update_one({"user_id": user_id}, {"$set": {"boost_active": False}})
        return {"message": "Boost d\u00e9sactiv\u00e9", "boost_active": False}
    else:
        now = datetime.now(timezone.utc)
        await db.dj_profiles.update_one({"user_id": user_id}, {"$set": {
            "boost_active": True, "boost_start": now,
            "boost_end": now + timedelta(days=30), "boost_plan": "admin_free",
        }})
        return {"message": "Boost activ\u00e9 (30 jours)", "boost_active": True}


@router.delete("/admin/djs/{user_id}")
async def admin_delete_dj(user_id: str, request: Request):
    """Admin: Delete a DJ profile"""
    await require_admin(request)
    result = await db.dj_profiles.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="DJ non trouv\u00e9")
    return {"message": "DJ supprim\u00e9 avec succ\u00e8s"}


@router.post("/admin/djs/{user_id}/send-reminder")
async def admin_send_reminder(user_id: str, request: Request):
    """Admin: Send payment reminder email to a specific DJ"""
    await require_admin(request)
    from routes.notifications import send_email, build_reminder_email
    dj = await db.dj_profiles.find_one({"user_id": user_id})
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouvé")
    user = await db.users.find_one({"user_id": user_id})
    if not user or not user.get("email"):
        raise HTTPException(status_code=400, detail="Pas d'email pour ce DJ")
    email = user["email"]
    dj_name = dj.get("nom_de_scene") or dj.get("prenom") or "DJ"
    subject = f"🎧 {dj_name}, reactivez votre profil DJ Match !"
    html = build_reminder_email(dj_name, "", True)
    success = send_email(email, subject, html)
    if success:
        await db.email_logs.insert_one({
            "user_id": user_id, "email": email,
            "reminder_type": "admin_manual",
            "subject": subject,
            "sent_at": datetime.now(timezone.utc),
        })
        return {"message": f"Relance envoyée à {email}", "success": True}
    else:
        raise HTTPException(status_code=500, detail="Erreur d'envoi email")
