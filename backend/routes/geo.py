from fastapi import APIRouter
from typing import Optional
from datetime import datetime, timezone

from database import db
from france_geo import (
    get_all_regions, get_all_departments, get_departments_by_region,
    get_department_for_city
)

router = APIRouter()


@router.get("/geo/regions")
async def get_regions():
    """Get all French regions"""
    return get_all_regions()


@router.get("/geo/departments")
async def get_departments(region_code: Optional[str] = None):
    """Get all French departments, optionally filtered by region"""
    if region_code:
        return get_departments_by_region(region_code)
    return get_all_departments()


@router.get("/geo/lookup-city")
async def lookup_city(city: str):
    """Lookup city information (department, region, coordinates)"""
    result = get_department_for_city(city)
    if result:
        return result
    return {"error": "Ville non trouv\u00e9e", "city": city}


@router.get("/geo/djs-map")
async def get_djs_for_map(
    region_code: Optional[str] = None,
    department_code: Optional[str] = None,
    type_evenement: Optional[str] = None,
    verifie_uniquement: bool = False
):
    """Get DJ locations for map display (only active and subscribed DJs)"""
    query = {"is_active": True, "subscription_status": {"$in": ["active", "trial"]}}
    if region_code:
        query["region_code"] = region_code
    if department_code:
        query["department_code"] = department_code
    if type_evenement:
        query["types_evenements"] = {"$in": [type_evenement]}
    if verifie_uniquement:
        query["badge_verifie"] = True
    query["latitude"] = {"$ne": None}
    query["longitude"] = {"$ne": None}
    djs = await db.dj_profiles.find(query, {
        "_id": 0, "user_id": 1, "nom_de_scene": 1, "ville": 1,
        "department_name": 1, "region_name": 1, "latitude": 1, "longitude": 1,
        "photo_profil": 1, "note_moyenne": 1, "badge_verifie": 1,
        "tarif_indicatif": 1, "types_evenements": 1
    }).to_list(500)
    return {"total": len(djs), "djs": djs}
