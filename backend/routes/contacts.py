from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
import uuid

from database import db
from auth import require_dj
from models import ContactRequest

router = APIRouter()


@router.post("/contact")
async def create_contact_request(contact: ContactRequest):
    """Create a contact request for a DJ"""
    dj = await db.dj_profiles.find_one({
        "user_id": contact.dj_user_id, "is_active": True, "subscription_status": "active"
    })
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouv\u00e9 ou profil non visible")
    contact_dict = contact.dict()
    contact_dict["request_id"] = f"req_{uuid.uuid4().hex[:12]}"
    contact_dict["created_at"] = datetime.now(timezone.utc)
    contact_dict["status"] = "nouveau"
    contact_dict["read"] = False
    await db.contact_requests.insert_one(contact_dict)
    await db.dj_profiles.update_one({"user_id": contact.dj_user_id}, {"$inc": {"nombre_demandes": 1}})
    return {"message": "Demande envoy\u00e9e avec succ\u00e8s", "request_id": contact_dict["request_id"]}


@router.get("/dj/contacts")
async def get_dj_contacts(request: Request, status: Optional[str] = None):
    """Get contact requests for the DJ"""
    user_data = await require_dj(request)
    query = {"dj_user_id": user_data["user_id"]}
    if status:
        query["status"] = status
    contacts = await db.contact_requests.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return contacts


@router.put("/dj/contacts/{request_id}/read")
async def mark_contact_read(request_id: str, request: Request):
    """Mark a contact request as read"""
    user_data = await require_dj(request)
    result = await db.contact_requests.update_one(
        {"request_id": request_id, "dj_user_id": user_data["user_id"]}, {"$set": {"read": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Demande non trouv\u00e9e")
    return {"message": "Demande marqu\u00e9e comme lue"}


@router.delete("/dj/contacts/{request_id}")
async def delete_contact_request(request_id: str, request: Request):
    """Delete a contact request"""
    user_data = await require_dj(request)
    result = await db.contact_requests.delete_one(
        {"request_id": request_id, "dj_user_id": user_data["user_id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Demande non trouv\u00e9e")
    await db.dj_profiles.update_one(
        {"user_id": user_data["user_id"], "nombre_demandes": {"$gt": 0}},
        {"$inc": {"nombre_demandes": -1}}
    )
    return {"message": "Demande supprim\u00e9e"}
