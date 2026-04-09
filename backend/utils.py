import re
import base64
import uuid
from fastapi import HTTPException
from database import UPLOADS_DIR, logger

MINIMUM_TARIF = 800


def extract_price_from_tarif(tarif: str) -> int:
    """Extract numeric price from tarif string"""
    if not tarif:
        return 0
    numbers = re.findall(r'\d+', tarif.replace(' ', ''))
    if numbers:
        return int(numbers[0])
    return 0


def validate_minimum_tarif(tarif: str) -> tuple[bool, str]:
    """Validate that the tarif is at least MINIMUM_TARIF euros"""
    if not tarif or tarif.strip() == "":
        return False, f"Le tarif indicatif est obligatoire (minimum {MINIMUM_TARIF}\u20ac)"
    price = extract_price_from_tarif(tarif)
    if price < MINIMUM_TARIF:
        return False, f"Le tarif minimum doit \u00eatre de {MINIMUM_TARIF}\u20ac. Tarif d\u00e9tect\u00e9: {price}\u20ac"
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


def save_base64_image(base64_data: str, prefix: str = "img") -> str:
    """Save a base64-encoded image to disk and return the URL path."""
    try:
        if base64_data.startswith("data:"):
            header, encoded = base64_data.split(",", 1)
            if "png" in header:
                ext = "png"
            elif "webp" in header:
                ext = "webp"
            elif "gif" in header:
                ext = "gif"
            else:
                ext = "jpg"
        else:
            encoded = base64_data
            ext = "jpg"
        image_bytes = base64.b64decode(encoded)
        filename = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"
        filepath = UPLOADS_DIR / filename
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        return f"/api/uploads/{filename}"
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur de sauvegarde image: {str(e)}")


def convert_images_to_files(data: dict) -> dict:
    """Convert base64 images in a dict to file URLs. Modifies in place and returns."""
    if data.get("photo_profil") and data["photo_profil"].startswith("data:"):
        data["photo_profil"] = save_base64_image(data["photo_profil"], "profile")
    galerie = data.get("galerie_photos", [])
    if galerie:
        new_galerie = []
        for img in galerie:
            if img and img.startswith("data:"):
                new_galerie.append(save_base64_image(img, "gallery"))
            else:
                new_galerie.append(img)
        data["galerie_photos"] = new_galerie
    return data
