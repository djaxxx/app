from fastapi import HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
from database import db, ADMIN_EMAIL


async def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session token"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    if not session_token:
        return None
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        return None
    expires_at = session.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    return user


async def require_auth(request: Request) -> dict:
    """Require authentication"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifi\u00e9")
    return user


async def require_dj(request: Request) -> dict:
    """Require DJ profile"""
    user = await require_auth(request)
    dj_profile = await db.dj_profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not dj_profile:
        raise HTTPException(status_code=403, detail="Profil DJ requis")
    return {**user, "dj_profile": dj_profile}


async def require_admin(request: Request) -> dict:
    """Require admin access"""
    user = await require_auth(request)
    if user.get("email") != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Acc\u00e8s administrateur requis")
    return user
