from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum
import uuid


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


class SubscriptionPlan(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


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
    code_postal: Optional[str] = ""
    department_code: Optional[str] = ""
    department_name: Optional[str] = ""
    region_code: Optional[str] = ""
    region_name: Optional[str] = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    zone_intervention: List[str] = []
    departments_zones: List[str] = []
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
    status: str = "pending"
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
