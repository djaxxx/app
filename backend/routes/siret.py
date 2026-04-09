from fastapi import APIRouter
import httpx

from database import INSEE_API_KEY, logger
from models import SiretVerificationRequest, SiretVerificationResponse

router = APIRouter()


@router.post("/verify-siret", response_model=SiretVerificationResponse)
async def verify_siret(request: SiretVerificationRequest):
    """Verify SIRET number using INSEE API"""
    siret = request.siret.replace(" ", "").strip()
    if len(siret) != 14 or not siret.isdigit():
        return SiretVerificationResponse(valid=False, message="Le SIRET doit contenir exactement 14 chiffres")
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Accept": "application/json", "X-INSEE-Api-Key-Integration": INSEE_API_KEY}
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
                return SiretVerificationResponse(valid=True, company_name=denomination, address=adresse_str, activity=activite, message="SIRET valide")
            elif response.status_code == 404:
                return SiretVerificationResponse(valid=False, message="SIRET non trouv\u00e9 dans la base SIRENE")
            else:
                logger.error(f"INSEE API error: {response.status_code} - {response.text}")
                return SiretVerificationResponse(valid=False, message=f"Erreur de v\u00e9rification INSEE: {response.status_code}")
    except httpx.TimeoutException:
        return SiretVerificationResponse(valid=False, message="D\u00e9lai d'attente d\u00e9pass\u00e9 pour la v\u00e9rification SIRET")
    except Exception as e:
        logger.error(f"SIRET verification error: {str(e)}")
        return SiretVerificationResponse(valid=False, message="Erreur lors de la v\u00e9rification du SIRET")
