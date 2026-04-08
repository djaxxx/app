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
app = FastAPI(title="DJ Connect France API")

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
    photo_profil: Optional[str] = ""
    galerie_photos: List[str] = []
    galerie_videos: List[str] = []

class DJProfileUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    nom_de_scene: Optional[str] = None
    telephone: Optional[str] = None
    ville: Optional[str] = None
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
    client_telephone: str
    date_evenement: str
    lieu_evenement: str
    type_evenement: str
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

class Review(ReviewCreate):
    review_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:12]}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
    import re
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

# ===================
# API ROUTES
# ===================

@api_router.get("/")
async def root():
    return {"message": "DJ Connect France API", "version": "1.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

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

@api_router.get("/auth/me")
async def get_me(request: Request):
    """Get current user info"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    dj_profile = await db.dj_profiles.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    return {
        **user,
        "has_dj_profile": dj_profile is not None,
        "is_dj": dj_profile is not None,
        "dj_profile": dj_profile
    }

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
    
    # Verify SIRET
    siret_result = await verify_siret(SiretVerificationRequest(siret=profile_data.siret))
    if not siret_result.valid:
        raise HTTPException(status_code=400, detail=f"SIRET invalide: {siret_result.message}")
    
    # Validate minimum tarif
    tarif_valid, tarif_error = validate_minimum_tarif(profile_data.tarif_indicatif or "")
    if not tarif_valid:
        raise HTTPException(status_code=400, detail=tarif_error)
    
    # Create profile
    profile_dict = profile_data.dict()
    profile_dict["user_id"] = user["user_id"]
    profile_dict["email"] = user["email"]
    profile_dict["siret_verified"] = True
    profile_dict["company_name"] = siret_result.company_name or ""
    profile_dict["created_at"] = datetime.now(timezone.utc)
    profile_dict["updated_at"] = datetime.now(timezone.utc)
    profile_dict["subscription_status"] = "inactive"
    profile_dict["is_active"] = False  # Inactive until subscription
    profile_dict["note_moyenne"] = 0.0
    profile_dict["nombre_avis"] = 0
    profile_dict["nombre_vues"] = 0
    profile_dict["nombre_demandes"] = 0
    
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
    """Get DJ dashboard statistics"""
    user_data = await require_dj(request)
    profile = user_data["dj_profile"]
    user_id = user_data["user_id"]
    
    # Get contact requests count
    requests_count = await db.contact_requests.count_documents({"dj_user_id": user_id})
    unread_requests = await db.contact_requests.count_documents({"dj_user_id": user_id, "read": False})
    
    # Get recent reviews
    recent_reviews = await db.reviews.find({"dj_user_id": user_id}).sort("created_at", -1).limit(5).to_list(5)
    for review in recent_reviews:
        if "_id" in review:
            del review["_id"]
    
    return {
        "nombre_vues": profile.get("nombre_vues", 0),
        "nombre_demandes": requests_count,
        "demandes_non_lues": unread_requests,
        "note_moyenne": profile.get("note_moyenne", 0),
        "nombre_avis": profile.get("nombre_avis", 0),
        "profil_complete_percent": profile.get("profil_complete_percent", 0),
        "badge_verifie": profile.get("badge_verifie", False),
        "subscription_status": profile.get("subscription_status", "inactive"),
        "subscription_end_date": profile.get("subscription_end_date"),
        "recent_reviews": recent_reviews
    }

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
    
    if ville:
        query["$or"] = [
            {"ville": {"$regex": ville, "$options": "i"}},
            {"zone_intervention": {"$regex": ville, "$options": "i"}}
        ]
    
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
    """Get a specific DJ profile"""
    dj = await db.dj_profiles.find_one({"user_id": user_id, "is_active": True}, {"_id": 0})
    
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouvé")
    
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
    """Create a contact request for a DJ"""
    # Verify DJ exists
    dj = await db.dj_profiles.find_one({"user_id": contact.dj_user_id, "is_active": True})
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouvé")
    
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

# ===================
# REVIEWS
# ===================
@api_router.post("/reviews")
async def create_review(review_data: ReviewCreate):
    """Create a review for a DJ"""
    dj = await db.dj_profiles.find_one({"user_id": review_data.dj_user_id, "is_active": True})
    if not dj:
        raise HTTPException(status_code=404, detail="DJ non trouvé")
    
    review_dict = review_data.dict()
    review_dict["review_id"] = f"rev_{uuid.uuid4().hex[:12]}"
    review_dict["created_at"] = datetime.now(timezone.utc)
    review_dict["verified"] = False  # Admin verification required
    
    await db.reviews.insert_one(review_dict)
    
    # Update DJ rating
    all_reviews = await db.reviews.find({"dj_user_id": review_data.dj_user_id}).to_list(1000)
    total_notes = sum(r.get("note", 0) for r in all_reviews)
    avg_note = total_notes / len(all_reviews) if all_reviews else 0
    
    await db.dj_profiles.update_one(
        {"user_id": review_data.dj_user_id},
        {"$set": {"note_moyenne": round(avg_note, 1), "nombre_avis": len(all_reviews)}}
    )
    
    return {"message": "Avis soumis avec succès", "review_id": review_dict["review_id"]}

@api_router.get("/djs/{user_id}/reviews")
async def get_dj_reviews(user_id: str):
    """Get reviews for a DJ"""
    reviews = await db.reviews.find({"dj_user_id": user_id, "verified": True}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return reviews

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
    user = await require_auth(request)
    
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
