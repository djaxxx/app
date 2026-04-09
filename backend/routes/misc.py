from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "DJ Match France API", "version": "2.0.0"}


@router.get("/health")
async def health():
    return {"status": "healthy"}


@router.get("/event-types")
async def get_event_types():
    """Get list of event types"""
    return [
        {"id": "mariage", "label": "Mariage"},
        {"id": "anniversaire", "label": "Anniversaire"},
        {"id": "entreprise", "label": "\u00c9v\u00e9nement d'entreprise"},
        {"id": "soiree_privee", "label": "Soir\u00e9e priv\u00e9e"},
        {"id": "bar_mitzvah", "label": "Bar/Bat Mitzvah"},
        {"id": "festival", "label": "Festival"},
        {"id": "club", "label": "Club/Discoth\u00e8que"},
        {"id": "autre", "label": "Autre"}
    ]
