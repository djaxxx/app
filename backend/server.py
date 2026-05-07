"""
DJ Match France API - Main Server
Modular FastAPI application with routers.
"""
from fastapi import FastAPI, APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import traceback

from database import client, db, UPLOADS_DIR, logger
from routes.notifications import reminder_scheduler, check_and_send_trial_reminders

# Import all route modules
from routes.auth_routes import router as auth_router
from routes.upload import router as upload_router, migrate_base64_to_files
from routes.geo import router as geo_router
from routes.siret import router as siret_router
from routes.djs import router as djs_router
from routes.contacts import router as contacts_router
from routes.reviews import router as reviews_router
from routes.zones import router as zones_router
from routes.boost import router as boost_router
from routes.stripe import router as stripe_router
from routes.admin import router as admin_router
from routes.admin_contacts import router as admin_contacts_router
from routes.misc import router as misc_router

# Create the main app
app = FastAPI(title="DJ Match France API")

# Mount static files for uploaded images
app.mount("/api/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Create a single API router with /api prefix and include all sub-routers
api_router = APIRouter(prefix="/api")
api_router.include_router(misc_router)
api_router.include_router(auth_router)
api_router.include_router(upload_router)
api_router.include_router(geo_router)
api_router.include_router(siret_router)
api_router.include_router(djs_router)
api_router.include_router(contacts_router)
api_router.include_router(reviews_router)
api_router.include_router(zones_router)
api_router.include_router(boost_router)
api_router.include_router(stripe_router)
api_router.include_router(admin_router)
api_router.include_router(admin_contacts_router)

# Include the combined router
app.include_router(api_router)

# CORS middleware - echo back requesting origin for credential support
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origin_regex=r".*",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_migrate_images():
    """Auto-migrate base64 images to files on startup"""
    try:
        count = await db.dj_profiles.count_documents({
            "$or": [
                {"photo_profil": {"$regex": "^data:"}},
                {"galerie_photos": {"$elemMatch": {"$regex": "^data:"}}}
            ]
        })
        if count > 0:
            logger.info(f"Found {count} DJ profiles with base64 images. Starting migration...")
            migrated = await migrate_base64_to_files()
            logger.info(f"Migration complete: {migrated} profiles migrated.")
        else:
            logger.info("No base64 images to migrate.")
    except Exception as e:
        logger.error(f"Startup migration error: {e}")

    # Start background email reminder scheduler
    import asyncio
    asyncio.create_task(reminder_scheduler())
    logger.info("Email reminder scheduler started (every 6 hours)")


# Admin endpoint to manually trigger trial reminders
@app.post("/api/admin/send-trial-reminders")
async def admin_send_reminders(request: Request):
    from auth import require_admin
    await require_admin(request)
    sent = await check_and_send_trial_reminders()
    return {"message": f"{sent} rappel(s) envoye(s)"}


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# Global exception handler - catches ALL unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur. Veuillez réessayer."}
    )
