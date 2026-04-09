from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
import uuid
import httpx

from database import db, ADMIN_EMAIL, logger

router = APIRouter()


async def get_current_user(request: Request):
    """Get user from session token"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    session = await db.user_sessions.find_one({"session_token": session_token})
    if not session:
        return None
    if session.get("expires_at") and session["expires_at"] < datetime.now(timezone.utc):
        await db.user_sessions.delete_one({"session_token": session_token})
        return None
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    return user


async def find_or_merge_user(email: str) -> dict:
    """Find existing user by email. If multiple exist, merge them into one."""
    users = await db.users.find({"email": email}).to_list(10)
    if not users:
        return None
    if len(users) == 1:
        return users[0]
    # Multiple accounts for same email - merge into the one that has a DJ profile
    primary = None
    for u in users:
        dj = await db.dj_profiles.find_one({"user_id": u["user_id"]})
        if dj:
            primary = u
            break
    if not primary:
        primary = users[0]
    # Merge all other accounts into primary
    for u in users:
        if u["user_id"] != primary["user_id"]:
            old_id = u["user_id"]
            new_id = primary["user_id"]
            # Transfer password if primary doesn't have one
            if u.get("password_hash") and not primary.get("password_hash"):
                await db.users.update_one(
                    {"user_id": new_id},
                    {"$set": {"password_hash": u["password_hash"]}}
                )
                primary["password_hash"] = u["password_hash"]
            # Transfer sessions
            await db.user_sessions.update_many({"user_id": old_id}, {"$set": {"user_id": new_id}})
            # Transfer any orphaned DJ profiles
            await db.dj_profiles.update_many({"user_id": old_id}, {"$set": {"user_id": new_id}})
            # Transfer contact requests
            await db.contact_requests.update_many({"dj_user_id": old_id}, {"$set": {"dj_user_id": new_id}})
            # Delete duplicate user
            await db.users.delete_one({"user_id": old_id})
            logger.info(f"Merged user {old_id} into {new_id} for email {email}")
    return primary


@router.post("/auth/register-email")
async def register_email(request: Request, response: Response):
    """Register with email - merges with existing Google account if same email"""
    import bcrypt
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    name = body.get("name", "").strip()
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email et mot de passe requis")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caracteres")
    if not name:
        raise HTTPException(status_code=400, detail="Le nom est requis")

    existing = await find_or_merge_user(email)

    if existing:
        # Account exists (likely from Google OAuth) - add password and log in
        if existing.get("password_hash"):
            raise HTTPException(status_code=409, detail="Cet email est deja utilise. Connectez-vous plutot.")
        # Add password to existing account
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        await db.users.update_one(
            {"user_id": existing["user_id"]},
            {"$set": {"password_hash": hashed, "auth_method": "both", "updated_at": datetime.now(timezone.utc)}}
        )
        user_id = existing["user_id"]
        logger.info(f"Added password to existing Google account for {email}")
    else:
        # Brand new account
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "user_id": user_id, "email": email, "name": name,
            "password_hash": hashed, "auth_method": "email", "picture": None,
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
        })

    session_token = f"st_{uuid.uuid4().hex}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.user_sessions.delete_many({"user_id": user_id})
    await db.user_sessions.insert_one({
        "user_id": user_id, "session_token": session_token,
        "expires_at": expires_at, "created_at": datetime.now(timezone.utc),
    })
    response.set_cookie(key="session_token", value=session_token, httponly=True,
        secure=True, samesite="none", path="/", max_age=7*24*60*60)

    dj_profile = await db.dj_profiles.find_one({"user_id": user_id}, {"_id": 0})
    is_admin = ADMIN_EMAIL and email.lower() == ADMIN_EMAIL.lower()
    return {"user_id": user_id, "email": email, "name": existing.get("name", name) if existing else name,
            "picture": existing.get("picture") if existing else None,
            "has_dj_profile": dj_profile is not None, "is_dj": dj_profile is not None,
            "is_admin": is_admin}


@router.post("/auth/login-email")
async def login_email(request: Request, response: Response):
    """Login with email and password"""
    import bcrypt
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email et mot de passe requis")

    # Find and merge user if multiple accounts exist
    user = await find_or_merge_user(email)
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    user_id = user["user_id"]
    session_token = f"st_{uuid.uuid4().hex}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.user_sessions.delete_many({"user_id": user_id})
    await db.user_sessions.insert_one({
        "user_id": user_id, "session_token": session_token,
        "expires_at": expires_at, "created_at": datetime.now(timezone.utc),
    })
    response.set_cookie(key="session_token", value=session_token, httponly=True,
        secure=True, samesite="none", path="/", max_age=7*24*60*60)
    dj_profile = await db.dj_profiles.find_one({"user_id": user_id}, {"_id": 0})
    is_admin = ADMIN_EMAIL and user["email"].lower() == ADMIN_EMAIL.lower()
    return {"user_id": user_id, "email": user["email"], "name": user.get("name", ""),
            "picture": user.get("picture"), "has_dj_profile": dj_profile is not None,
            "is_dj": dj_profile is not None, "is_admin": is_admin}


@router.post("/auth/session")
async def create_session(request: Request, response: Response):
    """Exchange session_id for session_token (Google OAuth) - merges with existing email account"""
    body = await request.json()
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requis")
    try:
        async with httpx.AsyncClient() as client:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}, timeout=10.0
            )
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Session invalide")
            auth_data = auth_response.json()
            email = auth_data.get("email")
            name = auth_data.get("name")
            picture = auth_data.get("picture")
            session_token = auth_data.get("session_token")

            # Find existing user by email (could be email-registered)
            existing_user = await find_or_merge_user(email)

            if existing_user:
                user_id = existing_user["user_id"]
                await db.users.update_one({"user_id": user_id},
                    {"$set": {"name": name, "picture": picture, "updated_at": datetime.now(timezone.utc)}})
            else:
                user_id = f"user_{uuid.uuid4().hex[:12]}"
                await db.users.insert_one({
                    "user_id": user_id, "email": email, "name": name, "picture": picture,
                    "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)
                })

            expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            await db.user_sessions.delete_many({"user_id": user_id})
            await db.user_sessions.insert_one({
                "user_id": user_id, "session_token": session_token,
                "expires_at": expires_at, "created_at": datetime.now(timezone.utc)
            })
            response.set_cookie(key="session_token", value=session_token, httponly=True,
                secure=True, samesite="none", path="/", max_age=7*24*60*60)
            dj_profile = await db.dj_profiles.find_one({"user_id": user_id}, {"_id": 0})
            is_admin = ADMIN_EMAIL and email.lower() == ADMIN_EMAIL.lower()
            return {"user_id": user_id, "email": email, "name": name, "picture": picture,
                    "has_dj_profile": dj_profile is not None, "is_dj": dj_profile is not None,
                    "is_admin": is_admin}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Delai d'attente depasse")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur d'authentification")


@router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Deconnexion reussie"}


@router.get("/auth/me")
async def get_current_user_info(request: Request):
    """Get current user info including admin status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifie")
    is_admin = user.get("email") == ADMIN_EMAIL
    dj_profile = await db.dj_profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return {
        "user_id": user.get("user_id"), "email": user.get("email"),
        "name": user.get("name"), "picture": user.get("picture"),
        "is_admin": is_admin, "has_dj_profile": dj_profile is not None,
        "is_dj": dj_profile is not None, "dj_profile": dj_profile,
        "subscription_status": dj_profile.get("subscription_status") if dj_profile else None,
    }
