from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone, timedelta

from database import db, ADMIN_EMAIL
from auth import require_auth, require_dj
from models import DJProfileCreate, DJProfileUpdate, SiretVerificationRequest
from utils import validate_minimum_tarif, calculate_profile_completion, check_badge_verification, convert_images_to_files
from routes.siret import verify_siret
from france_geo import (
    get_department_for_city, get_info_by_postal_code,
    find_region_by_name, find_department_by_name
)

router = APIRouter()

TRIAL_DAYS = 15


def is_admin_user(user_data: dict) -> bool:
    """Check if the user is the admin"""
    return bool(ADMIN_EMAIL) and user_data.get("email", "").lower() == ADMIN_EMAIL.lower()


async def check_trial_expiry(profile: dict) -> dict:
    """Check if a trial has expired and update DB accordingly. Returns updated fields."""
    if profile.get("subscription_status") != "trial":
        return profile

    trial_end = profile.get("trial_end")
    if trial_end:
        te = trial_end if trial_end.tzinfo else trial_end.replace(tzinfo=timezone.utc)
        if te < datetime.now(timezone.utc):
            # Trial expired
            await db.dj_profiles.update_one(
                {"user_id": profile["user_id"]},
                {"$set": {
                    "subscription_status": "expired",
                    "is_active": False,
                }}
            )
            profile["subscription_status"] = "expired"
            profile["is_active"] = False
    return profile


@router.post("/dj/register")
async def register_dj(profile_data: DJProfileCreate, request: Request):
    """Register a new DJ (requires authentication and valid SIRET) - 15 day free trial"""
    user = await require_auth(request)
    existing = await db.dj_profiles.find_one({"user_id": user["user_id"]})
    if existing:
        raise HTTPException(status_code=400, detail="Vous avez deja un profil DJ")
    if not profile_data.siret or len(profile_data.siret.replace(" ", "")) != 14:
        raise HTTPException(status_code=400, detail="Le numero SIRET est obligatoire (14 chiffres)")
    siret_result = await verify_siret(SiretVerificationRequest(siret=profile_data.siret))
    if not siret_result.valid:
        raise HTTPException(status_code=400, detail=f"SIRET invalide - Inscription refusee: {siret_result.message}")
    tarif_valid, tarif_error = validate_minimum_tarif(profile_data.tarif_indicatif or "")
    if not tarif_valid:
        raise HTTPException(status_code=400, detail=tarif_error)
    geo_info = None
    code_postal = profile_data.code_postal or ""
    if code_postal.strip():
        geo_info = get_info_by_postal_code(code_postal.strip())
        if geo_info:
            profile_data.ville = geo_info.get("city", profile_data.ville)
    if not geo_info:
        geo_info = get_department_for_city(profile_data.ville)
    profile_dict = profile_data.dict()
    profile_dict["user_id"] = user["user_id"]
    profile_dict["email"] = profile_data.email or user.get("email", "")
    profile_dict["siret_verified"] = True
    profile_dict["company_name"] = siret_result.company_name or ""
    profile_dict["created_at"] = datetime.now(timezone.utc)
    profile_dict["updated_at"] = datetime.now(timezone.utc)

    # --- FREE TRIAL: 15 days ---
    now = datetime.now(timezone.utc)
    profile_dict["subscription_status"] = "trial"
    profile_dict["subscription_plan"] = "trial"
    profile_dict["is_active"] = True
    profile_dict["trial_start"] = now
    profile_dict["trial_end"] = now + timedelta(days=TRIAL_DAYS)

    profile_dict["note_moyenne"] = 0.0
    profile_dict["nombre_avis"] = 0
    profile_dict["nombre_vues"] = 0
    profile_dict["nombre_demandes"] = 0
    if geo_info:
        profile_dict["department_code"] = geo_info.get("department_code", "")
        profile_dict["department_name"] = geo_info.get("department_name", "")
        profile_dict["region_code"] = geo_info.get("region_code", "")
        profile_dict["region_name"] = geo_info.get("region_name", "")
        if not profile_dict.get("latitude"):
            profile_dict["latitude"] = geo_info.get("lat")
        if not profile_dict.get("longitude"):
            profile_dict["longitude"] = geo_info.get("lon")
        if geo_info.get("department_code"):
            profile_dict["departments_zones"] = [geo_info["department_code"]]
    profile_dict["profil_complete_percent"] = calculate_profile_completion(profile_dict)
    profile_dict["badge_verifie"] = check_badge_verification(profile_dict)
    convert_images_to_files(profile_dict)
    await db.dj_profiles.insert_one(profile_dict)
    if "_id" in profile_dict:
        del profile_dict["_id"]
    return {
        "message": "Profil DJ cree avec succes ! Essai gratuit de 15 jours active.",
        "profile": profile_dict,
        "trial": True,
        "trial_days": TRIAL_DAYS,
        "trial_end": profile_dict["trial_end"].isoformat(),
    }


@router.put("/dj/profile")
async def update_dj_profile(update_data: DJProfileUpdate, request: Request):
    """Update DJ profile"""
    user_data = await require_dj(request)
    user_id = user_data["user_id"]
    if update_data.tarif_indicatif is not None:
        tarif_valid, tarif_error = validate_minimum_tarif(update_data.tarif_indicatif)
        if not tarif_valid:
            raise HTTPException(status_code=400, detail=tarif_error)
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc)
    if update_data.ville:
        geo_info = get_department_for_city(update_data.ville)
        if geo_info:
            update_dict["department_code"] = geo_info.get("department_code", "")
            update_dict["department_name"] = geo_info.get("department_name", "")
            update_dict["region_code"] = geo_info.get("region_code", "")
            update_dict["region_name"] = geo_info.get("region_name", "")
            if not update_dict.get("latitude"):
                update_dict["latitude"] = geo_info.get("lat")
            if not update_dict.get("longitude"):
                update_dict["longitude"] = geo_info.get("lon")
    current = await db.dj_profiles.find_one({"user_id": user_id}, {"_id": 0})
    merged = {**current, **update_dict}
    update_dict["profil_complete_percent"] = calculate_profile_completion(merged)
    update_dict["badge_verifie"] = check_badge_verification(merged)
    convert_images_to_files(update_dict)
    await db.dj_profiles.update_one({"user_id": user_id}, {"$set": update_dict})
    updated = await db.dj_profiles.find_one({"user_id": user_id}, {"_id": 0})
    return {"message": "Profil mis a jour", "profile": updated}


@router.get("/dj/profile")
async def get_my_dj_profile(request: Request):
    """Get current user's DJ profile"""
    user_data = await require_dj(request)
    return user_data["dj_profile"]


@router.get("/dj/dashboard")
async def get_dj_dashboard(request: Request):
    """Get DJ dashboard statistics - handles trial, active, admin"""
    user_data = await require_dj(request)
    profile = user_data["dj_profile"]
    user_id = user_data["user_id"]
    admin = is_admin_user(user_data)

    # Admin override: always active, never locked
    if admin:
        update_fields = {}
        if profile.get("subscription_status") != "active":
            update_fields["subscription_status"] = "active"
            update_fields["subscription_plan"] = "admin_permanent"
            update_fields["is_active"] = True
        if not profile.get("boost_active") or profile.get("boost_active") is False:
            update_fields["boost_active"] = "Permanent"
            update_fields["boost_plan"] = "admin_permanent"
        if update_fields:
            await db.dj_profiles.update_one({"user_id": user_id}, {"$set": update_fields})

        requests_count = await db.contact_requests.count_documents({"dj_user_id": user_id})
        unread_requests = await db.contact_requests.count_documents({"dj_user_id": user_id, "read": False})
        recent_reviews = await db.reviews.find({"dj_user_id": user_id, "status": "approved"}).sort("created_at", -1).limit(5).to_list(5)
        for review in recent_reviews:
            if "_id" in review:
                del review["_id"]
        pending_reviews_count = await db.reviews.count_documents({"dj_user_id": user_id, "status": "pending"})
        return {
            "subscription_status": "active",
            "subscription_plan": "admin_permanent",
            "subscription_end_date": None,
            "profil_complete_percent": profile.get("profil_complete_percent", 0),
            "badge_verifie": profile.get("badge_verifie", False),
            "is_locked": False,
            "is_admin": True,
            "nombre_vues": profile.get("nombre_vues", 0),
            "nombre_demandes": requests_count,
            "demandes_non_lues": unread_requests,
            "note_moyenne": profile.get("note_moyenne", 0),
            "nombre_avis": profile.get("nombre_avis", 0),
            "recent_reviews": recent_reviews,
            "pending_reviews_count": pending_reviews_count,
        }

    # Check trial expiry
    profile = await check_trial_expiry(profile)
    subscription_status = profile.get("subscription_status", "inactive")

    # Trial info
    trial_info = {}
    if subscription_status == "trial":
        trial_end = profile.get("trial_end")
        if trial_end:
            days_left = max(0, (trial_end - datetime.now(timezone.utc)).days)
            trial_info = {
                "is_trial": True,
                "trial_end": trial_end.isoformat() if hasattr(trial_end, 'isoformat') else str(trial_end),
                "trial_days_remaining": days_left,
            }

    # Determine if locked
    is_visible = subscription_status in ("active", "trial")

    base_response = {
        "subscription_status": subscription_status,
        "subscription_plan": profile.get("subscription_plan"),
        "subscription_end_date": profile.get("subscription_end_date"),
        "profil_complete_percent": profile.get("profil_complete_percent", 0),
        "badge_verifie": profile.get("badge_verifie", False),
        "is_locked": not is_visible,
        "is_admin": False,
        **trial_info,
    }

    if not is_visible:
        base_response.update({
            "nombre_vues": 0, "nombre_demandes": 0, "demandes_non_lues": 0,
            "note_moyenne": 0, "nombre_avis": 0, "recent_reviews": [],
            "lock_message": "Votre essai gratuit est termine. Choisissez une formule pour rester visible sur la plateforme.",
        })
        return base_response

    requests_count = await db.contact_requests.count_documents({"dj_user_id": user_id})
    unread_requests = await db.contact_requests.count_documents({"dj_user_id": user_id, "read": False})
    recent_reviews = await db.reviews.find({"dj_user_id": user_id, "status": "approved"}).sort("created_at", -1).limit(5).to_list(5)
    for review in recent_reviews:
        if "_id" in review:
            del review["_id"]
    pending_reviews_count = await db.reviews.count_documents({"dj_user_id": user_id, "status": "pending"})
    base_response.update({
        "nombre_vues": profile.get("nombre_vues", 0),
        "nombre_demandes": requests_count,
        "demandes_non_lues": unread_requests,
        "note_moyenne": profile.get("note_moyenne", 0),
        "nombre_avis": profile.get("nombre_avis", 0),
        "recent_reviews": recent_reviews,
        "pending_reviews_count": pending_reviews_count,
    })
    return base_response


@router.get("/djs")
async def list_djs(
    ville: Optional[str] = None, code_postal: Optional[str] = None,
    type_evenement: Optional[str] = None, budget_max: Optional[int] = None,
    note_min: Optional[float] = None, verifie_uniquement: bool = False,
    page: int = 1, limit: int = 20
):
    """List active DJs with filters - includes trial DJs"""
    query = {"is_active": True, "subscription_status": {"$in": ["active", "trial"]}}
    search_term = code_postal or ville
    if search_term and search_term.strip():
        search_term = search_term.strip()
        search_conditions = []
        if search_term.isdigit() and len(search_term) == 5:
            postal_info = get_info_by_postal_code(search_term)
            if postal_info:
                dept_code = postal_info["department_code"]
                search_conditions.append({"departments_zones": dept_code})
                search_conditions.append({"department_code": dept_code})
        elif len(search_term) >= 2:
            search_conditions = [
                {"ville": {"$regex": search_term, "$options": "i"}},
                {"zone_intervention": {"$regex": search_term, "$options": "i"}},
                {"region_name": {"$regex": search_term, "$options": "i"}},
                {"department_name": {"$regex": search_term, "$options": "i"}},
            ]
            if len(search_term) >= 3:
                region_match = find_region_by_name(search_term)
                if region_match:
                    search_conditions.append({"region_code": region_match["code"]})
                dept_match = find_department_by_name(search_term)
                if dept_match:
                    search_conditions.append({"department_code": dept_match["code"]})
                geo_info = get_department_for_city(search_term)
                if geo_info:
                    if geo_info.get("department_code"):
                        search_conditions.append({"department_code": geo_info["department_code"]})
                    if geo_info.get("region_code"):
                        search_conditions.append({"region_code": geo_info["region_code"]})
        if search_conditions:
            query["$or"] = search_conditions
    if type_evenement:
        query["types_evenements"] = {"$in": [type_evenement]}
    if note_min:
        query["note_moyenne"] = {"$gte": note_min}
    if verifie_uniquement:
        query["badge_verifie"] = True
    skip = (page - 1) * limit
    total = await db.dj_profiles.count_documents(query)
    now = datetime.now(timezone.utc)
    djs = await db.dj_profiles.find(query, {"_id": 0}).sort([
        ("boost_active", -1), ("note_moyenne", -1),
    ]).skip(skip).limit(limit).to_list(limit)

    expired_ids = []
    for dj in djs:
        dj.pop("telephone", None)
        dj.pop("email", None)
        dj.pop("assurance_rc_numero", None)
        dj.pop("assurance_rc_organisme", None)
        if "boost_active" not in dj:
            dj["boost_active"] = False
        boost_end = dj.get("boost_end")
        if dj.get("boost_active") and boost_end:
            be = boost_end if boost_end.tzinfo else boost_end.replace(tzinfo=timezone.utc)
            if be < now:
                dj["boost_active"] = False
                await db.dj_profiles.update_one({"user_id": dj["user_id"]}, {"$set": {"boost_active": False}})
        # Check trial expiry inline
        if dj.get("subscription_status") == "trial":
            trial_end = dj.get("trial_end")
            te = trial_end.replace(tzinfo=timezone.utc) if trial_end and not trial_end.tzinfo else trial_end
            if te and te < now:
                expired_ids.append(dj["user_id"])

    # Remove expired trial DJs from results
    if expired_ids:
        await db.dj_profiles.update_many(
            {"user_id": {"$in": expired_ids}},
            {"$set": {"subscription_status": "expired", "is_active": False}}
        )
        djs = [dj for dj in djs if dj.get("user_id") not in expired_ids]
        total -= len(expired_ids)

    return {"total": total, "page": page, "limit": limit, "pages": max(1, (total + limit - 1) // limit), "djs": djs}


@router.get("/djs/{user_id}")
async def get_dj_profile(user_id: str):
    """Get a specific DJ profile - visible for active and trial DJs"""
    dj = await db.dj_profiles.find_one(
        {"user_id": user_id, "is_active": True, "subscription_status": {"$in": ["active", "trial"]}},
        {"_id": 0}
    )
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouve ou profil non visible")

    # Check trial expiry
    if dj.get("subscription_status") == "trial":
        trial_end = dj.get("trial_end")
        if trial_end:
            te = trial_end if trial_end.tzinfo else trial_end.replace(tzinfo=timezone.utc)
            if te < datetime.now(timezone.utc):
                await db.dj_profiles.update_one(
                    {"user_id": user_id},
                    {"$set": {"subscription_status": "expired", "is_active": False}}
                )
                raise HTTPException(status_code=404, detail="DJ non trouve ou profil non visible")

    await db.dj_profiles.update_one({"user_id": user_id}, {"$inc": {"nombre_vues": 1}})
    reviews = await db.reviews.find({"dj_user_id": user_id, "verified": True}).sort("created_at", -1).limit(10).to_list(10)
    for review in reviews:
        if "_id" in review:
            del review["_id"]
    dj_public = {**dj}
    dj_public["reviews"] = reviews
    dj_public.pop("assurance_rc_numero", None)
    dj_public.pop("assurance_rc_organisme", None)
    return dj_public
