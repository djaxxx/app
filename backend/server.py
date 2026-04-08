from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
from enum import Enum
import re

# Import French geographic data
from france_geo import (
    REGIONS_FRANCE, DEPARTMENTS_FRANCE, MAJOR_CITIES_FRANCE,
    get_department_for_city, get_all_regions, get_all_departments,
    get_departments_by_region, find_region_by_name, find_department_by_name
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# API Keys
INSEE_API_KEY = os.environ.get('INSEE_API_KEY', '')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

# Create the main app
app = FastAPI(title="DJ Match France API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===================
# ENUMS
# ===================
class EventType(str, Enum):
    MARIAGE = "mariage"
    ANNIVERSAIRE = "anniversaire"
    ENTREPRISE = "entreprise"
    SOIREE_PRIVEE = "soiree_privee"
    BAR_MITZVAH = "bar_mitzvah"
    FESTIVAL = "festival"
    CLUB = "club"
    AUTRE = "autre"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    CANCELLED = "cancelled"

# ===================
# PYDANTIC MODELS
# ===================
class SiretVerificationRequest(BaseModel):
    siret: str

class SiretVerificationResponse(BaseModel):
    valid: bool
    company_name: Optional[str] = None
    address: Optional[str] = None
    activity: Optional[str] = None
    message: Optional[str] = None

class DJProfileCreate(BaseModel):
    email: EmailStr
    nom: str
    prenom: str
    nom_de_scene: str
    telephone: str
    ville: str
    department_code: Optional[str] = ""
    department_name: Optional[str] = ""
    region_code: Optional[str] = ""
    region_name: Optional[str] = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    zone_intervention: List[str] = []
    siret: str
    description: Optional[str] = ""
    annees_experience: Optional[int] = 0
    types_evenements: List[str] = []
    materiel_son: Optional[str] = ""
    materiel_lumiere: Optional[str] = ""
    options_supplementaires: Optional[str] = ""
    tarif_indicatif: Optional[str] = ""
    instagram: Optional[str] = ""
    tiktok: Optional[str] = ""
    youtube: Optional[str] = ""
    google_page: Optional[str] = ""
    site_internet: Optional[str] = ""
    photo_profil: Optional[str] = ""
    galerie_photos: List[str] = []
    galerie_videos: List[str] = []

class DJProfileUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    nom_de_scene: Optional[str] = None
    telephone: Optional[str] = None
    ville: Optional[str] = None
    department_code: Optional[str] = None
    department_name: Optional[str] = None
    region_code: Optional[str] = None
    region_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    zone_intervention: Optional[List[str]] = None
    description: Optional[str] = None
    annees_experience: Optional[int] = None
    types_evenements: Optional[List[str]] = None
    materiel_son: Optional[str] = None
    materiel_lumiere: Optional[str] = None
    options_supplementaires: Optional[str] = None
    tarif_indicatif: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    youtube: Optional[str] = None
    google_page: Optional[str] = None
    site_internet: Optional[str] = None
    photo_profil: Optional[str] = None
    galerie_photos: Optional[List[str]] = None
    galerie_videos: Optional[List[str]] = None

class DJProfile(BaseModel):
    user_id: str
    email: str
    nom: str
    prenom: str
    nom_de_scene: str
    telephone: str
    ville: str
    zone_intervention: List[str] = []
    siret: str
    siret_verified: bool = False
    company_name: Optional[str] = ""
    description: str = ""
    annees_experience: int = 0
    types_evenements: List[str] = []
    materiel_son: str = ""
    materiel_lumiere: str = ""
    options_supplementaires: str = ""
    tarif_indicatif: str = ""
    instagram: str = ""
    tiktok: str = ""
    youtube: str = ""
    google_page: str = ""
    site_internet: str = ""
    photo_profil: str = ""
    galerie_photos: List[str] = []
    galerie_videos: List[str] = []
    note_moyenne: float = 0.0
    nombre_avis: int = 0
    nombre_vues: int = 0
    nombre_demandes: int = 0
    badge_verifie: bool = False
    profil_complete_percent: int = 0
    subscription_status: str = "inactive"
    subscription_end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class ContactRequest(BaseModel):
    dj_user_id: str
    client_nom: str
    client_email: EmailStr
    client_telephone: Optional[str] = ""
    date_evenement: Optional[str] = ""
    lieu_evenement: Optional[str] = ""
    type_evenement: Optional[str] = ""
    message: str

class ContactRequestDB(ContactRequest):
    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "nouveau"
    read: bool = False

class ReviewCreate(BaseModel):
    dj_user_id: str
    client_nom: str
    client_email: EmailStr
    note: int = Field(ge=1, le=5)
    commentaire: str
    type_evenement: Optional[str] = ""
    date_evenement: Optional[str] = ""

class Review(ReviewCreate):
    review_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:12]}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"  # pending, approved, rejected
    verified: bool = False

class DJSearchFilters(BaseModel):
    ville: Optional[str] = None
    departement: Optional[str] = None
    region: Optional[str] = None
    type_evenement: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    note_min: Optional[float] = None
    verifie_uniquement: bool = False
    disponible_date: Optional[str] = None

# ===================
# HELPER FUNCTIONS
# ===================
MINIMUM_TARIF = 800  # Minimum price in euros

def extract_price_from_tarif(tarif: str) -> int:
    """Extract numeric price from tarif string"""
    if not tarif:
        return 0
    # Remove common words and extract numbers
    numbers = re.findall(r'\d+', tarif.replace(' ', ''))
    if numbers:
        return int(numbers[0])
    return 0

def validate_minimum_tarif(tarif: str) -> tuple[bool, str]:
    """Validate that the tarif is at least MINIMUM_TARIF euros"""
    if not tarif or tarif.strip() == "":
        return False, f"Le tarif indicatif est obligatoire (minimum {MINIMUM_TARIF}€)"
    
    price = extract_price_from_tarif(tarif)
    if price < MINIMUM_TARIF:
        return False, f"Le tarif minimum doit être de {MINIMUM_TARIF}€. Tarif détecté: {price}€"
    
    return True, ""

def calculate_profile_completion(profile: dict) -> int:
    """Calculate profile completion percentage"""
    required_fields = ['nom', 'prenom', 'nom_de_scene', 'telephone', 'ville', 'siret', 'description']
    optional_fields = ['annees_experience', 'types_evenements', 'materiel_son', 'materiel_lumiere',
                       'tarif_indicatif', 'instagram', 'tiktok', 'youtube', 'photo_profil', 
                       'galerie_photos', 'zone_intervention']
    
    total_fields = len(required_fields) + len(optional_fields)
    filled_fields = 0
    
    for field in required_fields:
        if profile.get(field):
            filled_fields += 1
    
    for field in optional_fields:
        value = profile.get(field)
        if value:
            if isinstance(value, list) and len(value) > 0:
                filled_fields += 1
            elif isinstance(value, str) and value.strip():
                filled_fields += 1
            elif isinstance(value, int) and value > 0:
                filled_fields += 1
    
    return int((filled_fields / total_fields) * 100)

def check_badge_verification(profile: dict) -> bool:
    """Check if DJ qualifies for verified badge"""
    siret_verified = profile.get('siret_verified', False)
    profile_percent = profile.get('profil_complete_percent', 0)
    return siret_verified and profile_percent >= 80

# ===================
# AUTH HELPERS
# ===================
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
        raise HTTPException(status_code=401, detail="Non authentifié")
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
    admin_email = os.getenv("ADMIN_EMAIL", "")
    if user.get("email") != admin_email:
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    return user

# ===================
# API ROUTES
# ===================

@api_router.get("/")
async def root():
    return {"message": "DJ Match France API", "version": "1.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

# ===================
# GEOGRAPHIC DATA
# ===================
@api_router.get("/geo/regions")
async def get_regions():
    """Get all French regions"""
    return get_all_regions()

@api_router.get("/geo/departments")
async def get_departments(region_code: Optional[str] = None):
    """Get all French departments, optionally filtered by region"""
    if region_code:
        return get_departments_by_region(region_code)
    return get_all_departments()

@api_router.get("/geo/lookup-city")
async def lookup_city(city: str):
    """Lookup city information (department, region, coordinates)"""
    result = get_department_for_city(city)
    if result:
        return result
    return {"error": "Ville non trouvée", "city": city}

@api_router.get("/geo/djs-map")
async def get_djs_for_map(
    region_code: Optional[str] = None,
    department_code: Optional[str] = None,
    type_evenement: Optional[str] = None,
    verifie_uniquement: bool = False
):
    """Get DJ locations for map display (only active and subscribed DJs)"""
    query = {"is_active": True, "subscription_status": "active"}
    
    if region_code:
        query["region_code"] = region_code
    if department_code:
        query["department_code"] = department_code
    if type_evenement:
        query["types_evenements"] = {"$in": [type_evenement]}
    if verifie_uniquement:
        query["badge_verifie"] = True
    
    # Only get DJs with coordinates
    query["latitude"] = {"$ne": None}
    query["longitude"] = {"$ne": None}
    
    # Project only necessary fields for map
    djs = await db.dj_profiles.find(query, {
        "_id": 0,
        "user_id": 1,
        "nom_de_scene": 1,
        "ville": 1,
        "department_name": 1,
        "region_name": 1,
        "latitude": 1,
        "longitude": 1,
        "photo_profil": 1,
        "note_moyenne": 1,
        "badge_verifie": 1,
        "tarif_indicatif": 1,
        "types_evenements": 1
    }).to_list(500)
    
    return {
        "total": len(djs),
        "djs": djs
    }

# ===================
# SIRET VERIFICATION
# ===================
@api_router.post("/verify-siret", response_model=SiretVerificationResponse)
async def verify_siret(request: SiretVerificationRequest):
    """Verify SIRET number using INSEE API"""
    siret = request.siret.replace(" ", "").strip()
    
    if len(siret) != 14 or not siret.isdigit():
        return SiretVerificationResponse(
            valid=False,
            message="Le SIRET doit contenir exactement 14 chiffres"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Accept": "application/json",
                "X-INSEE-Api-Key-Integration": INSEE_API_KEY
            }
            url = f"https://api.insee.fr/api-sirene/3.11/siret/{siret}"
            
            response = await client.get(url, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                etablissement = data.get("etablissement", {})
                unite_legale = etablissement.get("uniteLegale", {})
                adresse = etablissement.get("adresseEtablissement", {})
                
                denomination = unite_legale.get("denominationUniteLegale") or \
                              f"{unite_legale.get('prenomUsuelUniteLegale', '')} {unite_legale.get('nomUniteLegale', '')}".strip()
                
                adresse_str = f"{adresse.get('numeroVoieEtablissement', '')} {adresse.get('typeVoieEtablissement', '')} {adresse.get('libelleVoieEtablissement', '')}, {adresse.get('codePostalEtablissement', '')} {adresse.get('libelleCommuneEtablissement', '')}".strip()
                
                activite = etablissement.get("periodesEtablissement", [{}])[0].get("activitePrincipaleEtablissement", "")
                
                return SiretVerificationResponse(
                    valid=True,
                    company_name=denomination,
                    address=adresse_str,
                    activity=activite,
                    message="SIRET valide"
                )
            elif response.status_code == 404:
                return SiretVerificationResponse(
                    valid=False,
                    message="SIRET non trouvé dans la base SIRENE"
                )
            else:
                logger.error(f"INSEE API error: {response.status_code} - {response.text}")
                return SiretVerificationResponse(
                    valid=False,
                    message=f"Erreur de vérification INSEE: {response.status_code}"
                )
    except httpx.TimeoutException:
        return SiretVerificationResponse(
            valid=False,
            message="Délai d'attente dépassé pour la vérification SIRET"
        )
    except Exception as e:
        logger.error(f"SIRET verification error: {str(e)}")
        return SiretVerificationResponse(
            valid=False,
            message="Erreur lors de la vérification du SIRET"
        )

# ===================
# AUTHENTICATION
# ===================
@api_router.post("/auth/session")
async def create_session(request: Request, response: Response):
    """Exchange session_id for session_token"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id requis")
    
    try:
        async with httpx.AsyncClient() as client:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Session invalide")
            
            auth_data = auth_response.json()
            email = auth_data.get("email")
            name = auth_data.get("name")
            picture = auth_data.get("picture")
            session_token = auth_data.get("session_token")
            
            # Find or create user
            existing_user = await db.users.find_one({"email": email}, {"_id": 0})
            
            if existing_user:
                user_id = existing_user["user_id"]
                await db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {"name": name, "picture": picture, "updated_at": datetime.now(timezone.utc)}}
                )
            else:
                user_id = f"user_{uuid.uuid4().hex[:12]}"
                await db.users.insert_one({
                    "user_id": user_id,
                    "email": email,
                    "name": name,
                    "picture": picture,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                })
            
            # Create session
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            await db.user_sessions.delete_many({"user_id": user_id})
            await db.user_sessions.insert_one({
                "user_id": user_id,
                "session_token": session_token,
                "expires_at": expires_at,
                "created_at": datetime.now(timezone.utc)
            })
            
            # Set cookie
            response.set_cookie(
                key="session_token",
                value=session_token,
                httponly=True,
                secure=True,
                samesite="none",
                path="/",
                max_age=7 * 24 * 60 * 60
            )
            
            # Check if user has DJ profile
            dj_profile = await db.dj_profiles.find_one({"user_id": user_id}, {"_id": 0})
            
            return {
                "user_id": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "has_dj_profile": dj_profile is not None,
                "is_dj": dj_profile is not None
            }
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Délai d'attente dépassé")
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur d'authentification")

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Déconnexion réussie"}

# ===================
# DJ PROFILES
# ===================
@api_router.post("/dj/register")
async def register_dj(profile_data: DJProfileCreate, request: Request):
    """Register a new DJ (requires authentication and valid SIRET)"""
    user = await require_auth(request)
    
    # Check if user already has a DJ profile
    existing = await db.dj_profiles.find_one({"user_id": user["user_id"]})
    if existing:
        raise HTTPException(status_code=400, detail="Vous avez déjà un profil DJ")
    
    # Verify SIRET - MANDATORY
    if not profile_data.siret or len(profile_data.siret.replace(" ", "")) != 14:
        raise HTTPException(status_code=400, detail="Le numéro SIRET est obligatoire (14 chiffres)")
    
    siret_result = await verify_siret(SiretVerificationRequest(siret=profile_data.siret))
    if not siret_result.valid:
        raise HTTPException(status_code=400, detail=f"SIRET invalide - Inscription refusée: {siret_result.message}")
    
    # Validate minimum tarif - MANDATORY
    tarif_valid, tarif_error = validate_minimum_tarif(profile_data.tarif_indicatif or "")
    if not tarif_valid:
        raise HTTPException(status_code=400, detail=tarif_error)
    
    # Auto-geocode city if no coordinates provided
    geo_info = get_department_for_city(profile_data.ville)
    
    # Create profile
    profile_dict = profile_data.dict()
    profile_dict["user_id"] = user["user_id"]
    profile_dict["email"] = user["email"]
    profile_dict["siret_verified"] = True
    profile_dict["company_name"] = siret_result.company_name or ""
    profile_dict["created_at"] = datetime.now(timezone.utc)
    profile_dict["updated_at"] = datetime.now(timezone.utc)
    profile_dict["subscription_status"] = "inactive"
    profile_dict["is_active"] = False  # INACTIVE until payment
    profile_dict["note_moyenne"] = 0.0
    profile_dict["nombre_avis"] = 0
    profile_dict["nombre_vues"] = 0
    profile_dict["nombre_demandes"] = 0
    
    # Add geocoded data if found
    if geo_info:
        profile_dict["department_code"] = geo_info.get("department_code", "")
        profile_dict["department_name"] = geo_info.get("department_name", "")
        profile_dict["region_code"] = geo_info.get("region_code", "")
        profile_dict["region_name"] = geo_info.get("region_name", "")
        if not profile_dict.get("latitude"):
            profile_dict["latitude"] = geo_info.get("lat")
        if not profile_dict.get("longitude"):
            profile_dict["longitude"] = geo_info.get("lon")
    
    # Calculate completion and badge
    profile_dict["profil_complete_percent"] = calculate_profile_completion(profile_dict)
    profile_dict["badge_verifie"] = check_badge_verification(profile_dict)
    
    await db.dj_profiles.insert_one(profile_dict)
    
    # Return without _id
    if "_id" in profile_dict:
        del profile_dict["_id"]
    
    return {"message": "Profil DJ créé avec succès", "profile": profile_dict}

@api_router.put("/dj/profile")
async def update_dj_profile(update_data: DJProfileUpdate, request: Request):
    """Update DJ profile"""
    user_data = await require_dj(request)
    user_id = user_data["user_id"]
    
    # Validate minimum tarif if being updated
    if update_data.tarif_indicatif is not None:
        tarif_valid, tarif_error = validate_minimum_tarif(update_data.tarif_indicatif)
        if not tarif_valid:
            raise HTTPException(status_code=400, detail=tarif_error)
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc)
    
    # Auto-geocode city if ville is being updated
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
    
    # Get current profile to recalculate completion
    current = await db.dj_profiles.find_one({"user_id": user_id}, {"_id": 0})
    merged = {**current, **update_dict}
    update_dict["profil_complete_percent"] = calculate_profile_completion(merged)
    update_dict["badge_verifie"] = check_badge_verification(merged)
    
    await db.dj_profiles.update_one(
        {"user_id": user_id},
        {"$set": update_dict}
    )
    
    updated = await db.dj_profiles.find_one({"user_id": user_id}, {"_id": 0})
    return {"message": "Profil mis à jour", "profile": updated}

@api_router.get("/dj/profile")
async def get_my_dj_profile(request: Request):
    """Get current user's DJ profile"""
    user_data = await require_dj(request)
    return user_data["dj_profile"]

@api_router.get("/dj/dashboard")
async def get_dj_dashboard(request: Request):
    """Get DJ dashboard statistics - returns subscription_status for lock screen"""
    user_data = await require_dj(request)
    profile = user_data["dj_profile"]
    user_id = user_data["user_id"]
    
    subscription_status = profile.get("subscription_status", "inactive")
    
    # Always return subscription info
    base_response = {
        "subscription_status": subscription_status,
        "subscription_plan": profile.get("subscription_plan"),
        "subscription_end_date": profile.get("subscription_end_date"),
        "profil_complete_percent": profile.get("profil_complete_percent", 0),
        "badge_verifie": profile.get("badge_verifie", False),
        "is_locked": subscription_status != "active",
    }
    
    # If subscription inactive, return limited data
    if subscription_status != "active":
        base_response.update({
            "nombre_vues": 0,
            "nombre_demandes": 0,
            "demandes_non_lues": 0,
            "note_moyenne": 0,
            "nombre_avis": 0,
            "recent_reviews": [],
            "lock_message": "Votre profil est masqué. Activez votre abonnement pour être visible sur la plateforme.",
        })
        return base_response
    
    # Get contact requests count
    requests_count = await db.contact_requests.count_documents({"dj_user_id": user_id})
    unread_requests = await db.contact_requests.count_documents({"dj_user_id": user_id, "read": False})
    
    # Get recent reviews (approved only for stats)
    recent_reviews = await db.reviews.find({"dj_user_id": user_id, "status": "approved"}).sort("created_at", -1).limit(5).to_list(5)
    for review in recent_reviews:
        if "_id" in review:
            del review["_id"]
    
    # Count pending reviews
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

# ===================
# PUBLIC DJ LISTING
# ===================
@api_router.get("/djs")
async def list_djs(
    ville: Optional[str] = None,
    type_evenement: Optional[str] = None,
    budget_max: Optional[int] = None,
    note_min: Optional[float] = None,
    verifie_uniquement: bool = False,
    page: int = 1,
    limit: int = 20
):
    """List active DJs with filters"""
    query = {"is_active": True, "subscription_status": "active"}
    
    if ville and len(ville.strip()) >= 2:
        # Smart search: check city name, zone_intervention, region and department
        search_conditions = [
            {"ville": {"$regex": ville, "$options": "i"}},
            {"zone_intervention": {"$regex": ville, "$options": "i"}},
            {"region_name": {"$regex": ville, "$options": "i"}},
            {"department_name": {"$regex": ville, "$options": "i"}},
        ]
        
        # Check if search term is a known region name (only for terms >= 3 chars)
        if len(ville.strip()) >= 3:
            region_match = find_region_by_name(ville)
            if region_match:
                search_conditions.append({"region_code": region_match["code"]})
                search_conditions.append({"region_name": region_match["name"]})
            
            # Check if search term is a known department name
            dept_match = find_department_by_name(ville)
            if dept_match:
                search_conditions.append({"department_code": dept_match["code"]})
                search_conditions.append({"department_name": dept_match["name"]})
            
            # Also try to resolve the search term as a city via geo API
            geo_info = get_department_for_city(ville)
            if geo_info:
                # If the search term resolves to a city, also include DJs in the same department/region
                if geo_info.get("region_name"):
                    search_conditions.append({"region_name": geo_info["region_name"]})
                if geo_info.get("department_name"):
                    search_conditions.append({"department_name": geo_info["department_name"]})
                if geo_info.get("region_code"):
                    search_conditions.append({"region_code": geo_info["region_code"]})
                if geo_info.get("department_code"):
                    search_conditions.append({"department_code": geo_info["department_code"]})
        
        query["$or"] = search_conditions
    
    if type_evenement:
        query["types_evenements"] = {"$in": [type_evenement]}
    
    if note_min:
        query["note_moyenne"] = {"$gte": note_min}
    
    if verifie_uniquement:
        query["badge_verifie"] = True
    
    skip = (page - 1) * limit
    
    total = await db.dj_profiles.count_documents(query)
    djs = await db.dj_profiles.find(query, {"_id": 0}).sort("note_moyenne", -1).skip(skip).limit(limit).to_list(limit)
    
    # Remove sensitive data
    for dj in djs:
        dj.pop("telephone", None)
        dj.pop("email", None)
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "djs": djs
    }

@api_router.get("/djs/{user_id}")
async def get_dj_profile(user_id: str):
    """Get a specific DJ profile - only active subscribed DJs are visible"""
    dj = await db.dj_profiles.find_one(
        {"user_id": user_id, "is_active": True, "subscription_status": "active"},
        {"_id": 0}
    )
    
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouvé ou profil non visible (abonnement inactif)")
    
    # Increment view count
    await db.dj_profiles.update_one(
        {"user_id": user_id},
        {"$inc": {"nombre_vues": 1}}
    )
    
    # Get reviews
    reviews = await db.reviews.find({"dj_user_id": user_id, "verified": True}).sort("created_at", -1).limit(10).to_list(10)
    for review in reviews:
        if "_id" in review:
            del review["_id"]
    
    # Remove sensitive info for non-authenticated viewing
    dj_public = {**dj}
    dj_public["reviews"] = reviews
    
    return dj_public

# ===================
# CONTACT REQUESTS
# ===================
@api_router.post("/contact")
async def create_contact_request(contact: ContactRequest):
    """Create a contact request for a DJ (only active subscribed DJs)"""
    # Verify DJ exists and has active subscription
    dj = await db.dj_profiles.find_one({
        "user_id": contact.dj_user_id,
        "is_active": True,
        "subscription_status": "active"
    })
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouvé ou profil non visible")
    
    contact_dict = contact.dict()
    contact_dict["request_id"] = f"req_{uuid.uuid4().hex[:12]}"
    contact_dict["created_at"] = datetime.now(timezone.utc)
    contact_dict["status"] = "nouveau"
    contact_dict["read"] = False
    
    await db.contact_requests.insert_one(contact_dict)
    
    # Increment request count
    await db.dj_profiles.update_one(
        {"user_id": contact.dj_user_id},
        {"$inc": {"nombre_demandes": 1}}
    )
    
    return {"message": "Demande envoyée avec succès", "request_id": contact_dict["request_id"]}

@api_router.get("/dj/contacts")
async def get_dj_contacts(request: Request, status: Optional[str] = None):
    """Get contact requests for the DJ"""
    user_data = await require_dj(request)
    user_id = user_data["user_id"]
    
    query = {"dj_user_id": user_id}
    if status:
        query["status"] = status
    
    contacts = await db.contact_requests.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return contacts

@api_router.put("/dj/contacts/{request_id}/read")
async def mark_contact_read(request_id: str, request: Request):
    """Mark a contact request as read"""
    user_data = await require_dj(request)
    
    result = await db.contact_requests.update_one(
        {"request_id": request_id, "dj_user_id": user_data["user_id"]},
        {"$set": {"read": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    return {"message": "Demande marquée comme lue"}

@api_router.delete("/dj/contacts/{request_id}")
async def delete_contact_request(request_id: str, request: Request):
    """Delete a contact request"""
    user_data = await require_dj(request)
    
    result = await db.contact_requests.delete_one(
        {"request_id": request_id, "dj_user_id": user_data["user_id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Decrement request count
    await db.dj_profiles.update_one(
        {"user_id": user_data["user_id"], "nombre_demandes": {"$gt": 0}},
        {"$inc": {"nombre_demandes": -1}}
    )
    
    return {"message": "Demande supprimée"}

# ===================
# REVIEWS
# ===================
@api_router.post("/reviews")
async def create_review(review_data: ReviewCreate):
    """Create a review for a DJ — pending DJ approval"""
    dj = await db.dj_profiles.find_one({"user_id": review_data.dj_user_id, "is_active": True})
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouvé")
    
    review_dict = review_data.dict()
    review_dict["review_id"] = f"rev_{uuid.uuid4().hex[:12]}"
    review_dict["created_at"] = datetime.now(timezone.utc)
    review_dict["status"] = "pending"
    review_dict["verified"] = False
    
    await db.reviews.insert_one(review_dict)
    
    return {"message": "Merci ! Votre avis a été soumis et sera publié après validation par le DJ.", "review_id": review_dict["review_id"]}

@api_router.get("/djs/{user_id}/reviews")
async def get_dj_reviews(user_id: str):
    """Get approved reviews for a DJ (public)"""
    reviews = await db.reviews.find(
        {"dj_user_id": user_id, "status": "approved"},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return reviews

@api_router.get("/dj/reviews/pending")
async def get_pending_reviews(request: Request):
    """DJ: Get pending reviews awaiting approval"""
    user_data = await require_dj(request)
    user_id = user_data["user_id"]
    
    pending = await db.reviews.find(
        {"dj_user_id": user_id, "status": "pending"},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return {"reviews": pending, "count": len(pending)}

@api_router.get("/dj/reviews/all")
async def get_all_dj_reviews(request: Request):
    """DJ: Get all reviews (pending + approved + rejected)"""
    user_data = await require_dj(request)
    user_id = user_data["user_id"]
    
    all_reviews = await db.reviews.find(
        {"dj_user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    pending_count = sum(1 for r in all_reviews if r.get("status") == "pending")
    
    return {"reviews": all_reviews, "total": len(all_reviews), "pending_count": pending_count}

@api_router.put("/dj/reviews/{review_id}/approve")
async def approve_review(review_id: str, request: Request):
    """DJ: Approve a pending review"""
    user_data = await require_dj(request)
    user_id = user_data["user_id"]
    
    review = await db.reviews.find_one({"review_id": review_id, "dj_user_id": user_id})
    if not review:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    
    await db.reviews.update_one(
        {"review_id": review_id},
        {"$set": {"status": "approved", "verified": True}}
    )
    
    # Recalculate rating with only approved reviews
    approved_reviews = await db.reviews.find(
        {"dj_user_id": user_id, "status": "approved"},
        {"note": 1, "_id": 0}
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
    
    return {"message": "Avis approuvé et publié"}

@api_router.put("/dj/reviews/{review_id}/reject")
async def reject_review(review_id: str, request: Request):
    """DJ: Reject a pending review"""
    user_data = await require_dj(request)
    user_id = user_data["user_id"]
    
    review = await db.reviews.find_one({"review_id": review_id, "dj_user_id": user_id})
    if not review:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    
    await db.reviews.update_one(
        {"review_id": review_id},
        {"$set": {"status": "rejected", "verified": False}}
    )
    
    # Recalculate rating with only approved reviews
    approved_reviews = await db.reviews.find(
        {"dj_user_id": user_id, "status": "approved"},
        {"note": 1, "_id": 0}
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
    
    return {"message": "Avis rejeté"}

# ===================
# STRIPE SUBSCRIPTION
# ===================
class SubscriptionPlan(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"

SUBSCRIPTION_PRICES = {
    "monthly": {"amount": 8.00, "days": 30, "label": "Mensuel (8€/mois)"},
    "annual": {"amount": 80.00, "days": 365, "label": "Annuel (80€/an)"}
}

@api_router.get("/subscription/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return [
        {"id": "monthly", "amount": 8.00, "currency": "eur", "label": "Mensuel", "description": "8€/mois", "days": 30},
        {"id": "annual", "amount": 80.00, "currency": "eur", "label": "Annuel", "description": "80€/an (économisez 16€)", "days": 365}
    ]

@api_router.post("/subscription/create-checkout")
async def create_subscription_checkout(request: Request):
    """Create a Stripe checkout session for DJ subscription"""
    user_data = await require_dj(request)
    
    body = await request.json()
    origin_url = body.get("origin_url", "")
    plan = body.get("plan", "monthly")  # Default to monthly
    
    if not origin_url:
        raise HTTPException(status_code=400, detail="origin_url requis")
    
    if plan not in SUBSCRIPTION_PRICES:
        raise HTTPException(status_code=400, detail="Plan invalide")
    
    plan_details = SUBSCRIPTION_PRICES[plan]
    
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
        
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/webhook/stripe"
        
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        success_url = f"{origin_url}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/subscription/cancel"
        
        checkout_request = CheckoutSessionRequest(
            amount=plan_details["amount"],
            currency="eur",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user_data["user_id"],
                "type": "dj_subscription",
                "plan": plan,
                "days": str(plan_details["days"])
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        await db.payment_transactions.insert_one({
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
            "session_id": session.session_id,
            "user_id": user_data["user_id"],
            "amount": plan_details["amount"],
            "currency": "eur",
            "type": "subscription",
            "plan": plan,
            "days": plan_details["days"],
            "status": "pending",
            "payment_status": "initiated",
            "created_at": datetime.now(timezone.utc)
        })
        
        return {"checkout_url": session.url, "session_id": session.session_id, "plan": plan, "amount": plan_details["amount"]}
    
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création du paiement")

@api_router.get("/subscription/status/{session_id}")
async def get_subscription_status(session_id: str, request: Request):
    """Check subscription payment status"""
    await require_auth(request)
    
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {
                "status": status.status,
                "payment_status": status.payment_status,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # If paid, activate subscription
        if status.payment_status == "paid":
            transaction = await db.payment_transactions.find_one({"session_id": session_id})
            if transaction and transaction.get("status") != "completed":
                # Get days from transaction (default to 30 for monthly)
                days = transaction.get("days", 30)
                subscription_end = datetime.now(timezone.utc) + timedelta(days=days)
                
                await db.dj_profiles.update_one(
                    {"user_id": transaction["user_id"]},
                    {"$set": {
                        "subscription_status": "active",
                        "subscription_end_date": subscription_end,
                        "subscription_plan": transaction.get("plan", "monthly"),
                        "is_active": True
                    }}
                )
                
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {"status": "completed"}}
                )
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency
        }
    
    except Exception as e:
        logger.error(f"Subscription status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la vérification")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        body = await request.body()
        signature = request.headers.get("Stripe-Signature", "")
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            user_id = webhook_response.metadata.get("user_id")
            plan = webhook_response.metadata.get("plan", "monthly")
            days = int(webhook_response.metadata.get("days", "30"))
            if user_id:
                subscription_end = datetime.now(timezone.utc) + timedelta(days=days)
                
                await db.dj_profiles.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "subscription_status": "active",
                        "subscription_end_date": subscription_end,
                        "subscription_plan": plan,
                        "is_active": True
                    }}
                )
                
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {"$set": {"status": "completed", "payment_status": "paid"}}
                )
        
        return {"received": True}
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"received": True}  # Always return 200 to Stripe

# ===================
# ADMIN ENDPOINTS
# ===================

@api_router.get("/auth/me")
async def get_current_user_info(request: Request):
    """Get current user info including admin status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    admin_email = os.getenv("ADMIN_EMAIL", "")
    is_admin = user.get("email") == admin_email
    
    dj_profile = await db.dj_profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    return {
        "user_id": user.get("user_id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
        "is_admin": is_admin,
        "has_dj_profile": dj_profile is not None,
        "is_dj": dj_profile is not None,
        "dj_profile": dj_profile,
        "subscription_status": dj_profile.get("subscription_status") if dj_profile else None,
    }

@api_router.get("/admin/djs")
async def admin_list_djs(request: Request):
    """Admin: List ALL DJs (including inactive/unpaid)"""
    await require_admin(request)
    
    djs = await db.dj_profiles.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"djs": djs, "total": len(djs)}

@api_router.post("/admin/create-dj")
async def admin_create_dj(request: Request):
    """Admin: Create a DJ profile with free active subscription"""
    await require_admin(request)
    body = await request.json()
    
    # Generate a unique user_id for this DJ
    user_id = f"admin_dj_{uuid.uuid4().hex[:12]}"
    
    # Create user entry
    email = body.get("email", f"{user_id}@djmatch.fr")
    existing = await db.users.find_one({"email": email})
    if existing:
        user_id = existing["user_id"]
    else:
        await db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "name": body.get("nom_de_scene", "DJ"),
            "picture": "",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
    
    # Check if DJ profile already exists
    existing_dj = await db.dj_profiles.find_one({"user_id": user_id})
    if existing_dj:
        raise HTTPException(status_code=400, detail="Ce DJ existe déjà")
    
    # Auto-resolve geo
    city = body.get("ville", "")
    geo_data = {}
    if city:
        geo_result = get_department_for_city(city)
        if geo_result and "department_name" in geo_result:
            geo_data = geo_result
    
    # Create DJ profile with active subscription (FREE)
    now = datetime.now(timezone.utc)
    dj_data = {
        "user_id": user_id,
        "email": email,
        "nom": body.get("nom", ""),
        "prenom": body.get("prenom", ""),
        "nom_de_scene": body.get("nom_de_scene", ""),
        "telephone": body.get("telephone", ""),
        "siret": body.get("siret", ""),
        "siret_verified": True,  # Admin bypasses SIRET check
        "ville": city,
        "department_code": geo_data.get("department_code", body.get("department_code", "")),
        "department_name": geo_data.get("department_name", body.get("department_name", "")),
        "region_code": geo_data.get("region_code", body.get("region_code", "")),
        "region_name": geo_data.get("region_name", body.get("region_name", "")),
        "latitude": body.get("latitude"),
        "longitude": body.get("longitude"),
        "description": body.get("description", ""),
        "annees_experience": body.get("annees_experience", 0),
        "types_evenements": body.get("types_evenements", []),
        "materiel_son": body.get("materiel_son", ""),
        "materiel_lumiere": body.get("materiel_lumiere", ""),
        "tarif_indicatif": body.get("tarif_indicatif", "800"),
        "instagram": body.get("instagram", ""),
        "tiktok": body.get("tiktok", ""),
        "youtube": body.get("youtube", ""),
        "google_page": body.get("google_page", ""),
        "site_internet": body.get("site_internet", ""),
        "photo_profil": body.get("photo_profil", ""),
        "galerie_photos": body.get("galerie_photos", []),
        "subscription_status": "active",
        "subscription_plan": "admin_free",
        "subscription_end_date": (now + timedelta(days=36500)).isoformat(),  # ~100 years
        "is_active": True,
        "is_verified": True,
        "badge_verifie": True,
        "nombre_vues": 0,
        "nombre_avis": 0,
        "note_moyenne": 0,
        "created_at": now,
        "updated_at": now,
        "added_by_admin": True,
    }
    
    await db.dj_profiles.insert_one(dj_data)
    del dj_data["_id"]
    
    return {"message": "DJ créé avec succès (abonnement gratuit activé)", "dj": dj_data}

@api_router.put("/admin/djs/{user_id}/toggle-subscription")
async def admin_toggle_subscription(user_id: str, request: Request):
    """Admin: Toggle DJ subscription status (activate/deactivate for free)"""
    await require_admin(request)
    
    dj = await db.dj_profiles.find_one({"user_id": user_id})
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouvé")
    
    current_status = dj.get("subscription_status", "inactive")
    new_status = "inactive" if current_status == "active" else "active"
    
    update_data = {
        "subscription_status": new_status,
        "is_active": new_status == "active",
        "updated_at": datetime.now(timezone.utc),
    }
    
    if new_status == "active":
        update_data["subscription_plan"] = "admin_free"
        update_data["subscription_end_date"] = (datetime.now(timezone.utc) + timedelta(days=36500)).isoformat()
    
    await db.dj_profiles.update_one({"user_id": user_id}, {"$set": update_data})
    
    return {
        "message": f"DJ {'activé' if new_status == 'active' else 'désactivé'} avec succès",
        "subscription_status": new_status,
    }

@api_router.delete("/admin/djs/{user_id}")
async def admin_delete_dj(user_id: str, request: Request):
    """Admin: Delete a DJ profile"""
    await require_admin(request)
    
    result = await db.dj_profiles.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="DJ non trouvé")
    
    return {"message": "DJ supprimé avec succès"}

# ===================
# EVENT TYPES
# ===================
@api_router.get("/event-types")
async def get_event_types():
    """Get list of event types"""
    return [
        {"id": "mariage", "label": "Mariage"},
        {"id": "anniversaire", "label": "Anniversaire"},
        {"id": "entreprise", "label": "Événement d'entreprise"},
        {"id": "soiree_privee", "label": "Soirée privée"},
        {"id": "bar_mitzvah", "label": "Bar/Bat Mitzvah"},
        {"id": "festival", "label": "Festival"},
        {"id": "club", "label": "Club/Discothèque"},
        {"id": "autre", "label": "Autre"}
    ]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
