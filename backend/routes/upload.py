from fastapi import APIRouter, HTTPException, Request
from database import db, logger, UPLOADS_DIR
from auth import require_admin
from utils import save_base64_image

router = APIRouter()


@router.post("/upload/image")
async def upload_image(request: Request):
    """Upload a base64 image, save to disk, return URL."""
    body = await request.json()
    image_data = body.get("image", "")
    image_type = body.get("type", "gallery")
    if not image_data:
        raise HTTPException(status_code=400, detail="Aucune image fournie")
    if image_data.startswith("/api/uploads/") or image_data.startswith("http"):
        return {"url": image_data}
    prefix = "profile" if image_type == "profile" else "gallery"
    url = save_base64_image(image_data, prefix)
    return {"url": url}


@router.post("/upload/images")
async def upload_images(request: Request):
    """Upload multiple base64 images at once."""
    body = await request.json()
    images_data = body.get("images", [])
    image_type = body.get("type", "gallery")
    if not images_data:
        raise HTTPException(status_code=400, detail="Aucune image fournie")
    prefix = "profile" if image_type == "profile" else "gallery"
    urls = []
    for img in images_data:
        if img.startswith("/api/uploads/") or img.startswith("http"):
            urls.append(img)
        else:
            url = save_base64_image(img, prefix)
            urls.append(url)
    return {"urls": urls}


async def migrate_base64_to_files():
    """One-time migration: convert existing base64 images in MongoDB to files on disk."""
    try:
        cursor = db.dj_profiles.find({})
        migrated = 0
        async for dj in cursor:
            update_fields = {}
            photo = dj.get("photo_profil", "")
            if photo and photo.startswith("data:"):
                try:
                    url = save_base64_image(photo, "profile")
                    update_fields["photo_profil"] = url
                except Exception as e:
                    logger.error(f"Migration photo_profil failed for {dj.get('user_id')}: {e}")
            galerie = dj.get("galerie_photos", [])
            new_galerie = []
            galerie_changed = False
            for img in galerie:
                if img and img.startswith("data:"):
                    try:
                        url = save_base64_image(img, "gallery")
                        new_galerie.append(url)
                        galerie_changed = True
                    except Exception as e:
                        logger.error(f"Migration galerie failed for {dj.get('user_id')}: {e}")
                        new_galerie.append(img)
                else:
                    new_galerie.append(img)
            if galerie_changed:
                update_fields["galerie_photos"] = new_galerie
            if update_fields:
                await db.dj_profiles.update_one({"_id": dj["_id"]}, {"$set": update_fields})
                migrated += 1
                logger.info(f"Migrated images for DJ {dj.get('user_id', 'unknown')}")
        return migrated
    except Exception as e:
        logger.error(f"Migration error: {e}")
        return 0


@router.post("/admin/migrate-images")
async def admin_migrate_images(request: Request):
    """Admin: Migrate all existing base64 images to file storage."""
    await require_admin(request)
    migrated = await migrate_base64_to_files()
    return {"message": f"Migration termin\u00e9e: {migrated} profils DJ migr\u00e9s", "migrated_count": migrated}
