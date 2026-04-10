from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid

from database import db
from auth import require_dj
from models import ReviewCreate

router = APIRouter()


@router.post("/reviews")
async def create_review(review_data: ReviewCreate):
    """Create a review for a DJ"""
    dj = await db.dj_profiles.find_one({"user_id": review_data.dj_user_id, "is_active": True})
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouv\u00e9")
    review_dict = review_data.dict()
    review_dict["review_id"] = f"rev_{uuid.uuid4().hex[:12]}"
    review_dict["created_at"] = datetime.now(timezone.utc)
    review_dict["status"] = "pending"
    review_dict["verified"] = False
    await db.reviews.insert_one(review_dict)
    return {"message": "Merci ! Votre avis a \u00e9t\u00e9 soumis et sera publi\u00e9 apr\u00e8s validation par le DJ.", "review_id": review_dict["review_id"]}


@router.get("/djs/{user_id}/reviews")
async def get_dj_reviews(user_id: str, page: int = 1, limit: int = 50):
    """Get approved reviews for a DJ (public)"""
    skip = (page - 1) * limit
    total = await db.reviews.count_documents({"dj_user_id": user_id, "status": "approved"})
    reviews = await db.reviews.find(
        {"dj_user_id": user_id, "status": "approved"}, {"_id": 0}
    ).sort("created_at", -1).skip(skip).to_list(limit)
    return {"reviews": reviews, "total": total, "page": page, "limit": limit}


@router.get("/dj/reviews/pending")
async def get_pending_reviews(request: Request):
    """DJ: Get pending reviews awaiting approval"""
    user_data = await require_dj(request)
    pending = await db.reviews.find(
        {"dj_user_id": user_data["user_id"], "status": "pending"}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return {"reviews": pending, "count": len(pending)}


@router.get("/dj/reviews/all")
async def get_all_dj_reviews(request: Request):
    """DJ: Get all reviews"""
    user_data = await require_dj(request)
    all_reviews = await db.reviews.find(
        {"dj_user_id": user_data["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    pending_count = sum(1 for r in all_reviews if r.get("status") == "pending")
    return {"reviews": all_reviews, "total": len(all_reviews), "pending_count": pending_count}


async def _recalculate_rating(user_id: str):
    """Recalculate DJ rating from approved reviews"""
    approved_reviews = await db.reviews.find(
        {"dj_user_id": user_id, "status": "approved"}, {"note": 1, "_id": 0}
    ).to_list(1000)
    if approved_reviews:
        total = sum(r.get("note", 0) for r in approved_reviews)
        avg = total / len(approved_reviews)
    else:
        avg = 0
    await db.dj_profiles.update_one(
        {"user_id": user_id},
        {"$set": {"note_moyenne": round(avg, 1), "nombre_avis": len(approved_reviews)}}
    )


@router.put("/dj/reviews/{review_id}/approve")
async def approve_review(review_id: str, request: Request):
    """DJ: Approve a pending review"""
    user_data = await require_dj(request)
    review = await db.reviews.find_one({"review_id": review_id, "dj_user_id": user_data["user_id"]})
    if not review:
        raise HTTPException(status_code=404, detail="Avis non trouv\u00e9")
    await db.reviews.update_one({"review_id": review_id}, {"$set": {"status": "approved", "verified": True}})
    await _recalculate_rating(user_data["user_id"])
    return {"message": "Avis approuv\u00e9 et publi\u00e9"}


@router.put("/dj/reviews/{review_id}/reject")
async def reject_review(review_id: str, request: Request):
    """DJ: Reject a pending review"""
    user_data = await require_dj(request)
    review = await db.reviews.find_one({"review_id": review_id, "dj_user_id": user_data["user_id"]})
    if not review:
        raise HTTPException(status_code=404, detail="Avis non trouv\u00e9")
    await db.reviews.update_one({"review_id": review_id}, {"$set": {"status": "rejected", "verified": False}})
    await _recalculate_rating(user_data["user_id"])
    return {"message": "Avis rejet\u00e9"}
