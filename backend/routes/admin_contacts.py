from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from typing import Optional
import io
import csv

from database import db
from auth import require_admin

router = APIRouter()


@router.get("/admin/contacts")
async def admin_list_contacts(
    request: Request,
    type: Optional[str] = None,  # "dj" | "client" | None (all)
    status: Optional[str] = None,  # For DJs: "active" | "inactive" | For clients: "nouveau" | "lu"
    department: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
):
    """Admin: List all contacts (DJs + clients) with filters and segmentation."""
    await require_admin(request)

    contacts = []
    skip = (page - 1) * limit

    # ---- DJs ----
    if type != "client":
        dj_query = {}
        if status == "active":
            dj_query["subscription_status"] = "active"
        elif status == "inactive":
            dj_query["subscription_status"] = {"$ne": "active"}
        if department:
            dj_query["$or"] = [
                {"department_code": department},
                {"departments_zones": department},
            ]
        if search:
            dj_query["$or"] = dj_query.get("$or", []) + [
                {"nom_de_scene": {"$regex": search, "$options": "i"}},
                {"nom": {"$regex": search, "$options": "i"}},
                {"prenom": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"telephone": {"$regex": search, "$options": "i"}},
                {"ville": {"$regex": search, "$options": "i"}},
            ]

        djs = await db.dj_profiles.find(dj_query, {"_id": 0}).sort("created_at", -1).to_list(500)
        for dj in djs:
            contacts.append({
                "contact_type": "dj",
                "id": dj.get("user_id", ""),
                "nom": f"{dj.get('prenom', '')} {dj.get('nom', '')}".strip(),
                "nom_de_scene": dj.get("nom_de_scene", ""),
                "email": dj.get("email", ""),
                "telephone": dj.get("telephone", ""),
                "ville": dj.get("ville", ""),
                "code_postal": dj.get("code_postal", ""),
                "department_code": dj.get("department_code", ""),
                "department_name": dj.get("department_name", ""),
                "region_name": dj.get("region_name", ""),
                "subscription_status": dj.get("subscription_status", "inactive"),
                "subscription_plan": dj.get("subscription_plan", ""),
                "boost_active": dj.get("boost_active", False),
                "siret": dj.get("siret", ""),
                "assurance_rc_organisme": dj.get("assurance_rc_organisme", ""),
                "assurance_rc_numero": dj.get("assurance_rc_numero", ""),
                "tarif_indicatif": dj.get("tarif_indicatif", ""),
                "note_moyenne": dj.get("note_moyenne", 0),
                "nombre_avis": dj.get("nombre_avis", 0),
                "nombre_vues": dj.get("nombre_vues", 0),
                "instagram": dj.get("instagram", ""),
                "site_internet": dj.get("site_internet", ""),
                "created_at": dj.get("created_at", ""),
                "source": "inscription",
            })

    # ---- Clients (from contact_requests) ----
    if type != "dj":
        client_query = {}
        if status == "nouveau":
            client_query["read"] = False
        elif status == "lu":
            client_query["read"] = True
        if search:
            client_query["$or"] = [
                {"client_nom": {"$regex": search, "$options": "i"}},
                {"client_email": {"$regex": search, "$options": "i"}},
                {"client_telephone": {"$regex": search, "$options": "i"}},
                {"lieu_evenement": {"$regex": search, "$options": "i"}},
            ]

        requests = await db.contact_requests.find(client_query, {"_id": 0}).sort("created_at", -1).to_list(500)
        # Deduplicate by email
        seen_emails = set()
        for req in requests:
            email = req.get("client_email", "").lower()
            if email and email in seen_emails:
                continue
            seen_emails.add(email)
            contacts.append({
                "contact_type": "client",
                "id": req.get("request_id", ""),
                "nom": req.get("client_nom", ""),
                "nom_de_scene": "",
                "email": req.get("client_email", ""),
                "telephone": req.get("client_telephone", ""),
                "ville": req.get("lieu_evenement", ""),
                "code_postal": "",
                "department_code": "",
                "department_name": "",
                "region_name": "",
                "subscription_status": "",
                "subscription_plan": "",
                "boost_active": False,
                "siret": "",
                "assurance_rc_organisme": "",
                "assurance_rc_numero": "",
                "tarif_indicatif": "",
                "note_moyenne": 0,
                "nombre_avis": 0,
                "nombre_vues": 0,
                "instagram": "",
                "site_internet": "",
                "created_at": req.get("created_at", ""),
                "type_evenement": req.get("type_evenement", ""),
                "date_evenement": req.get("date_evenement", ""),
                "message": req.get("message", ""),
                "dj_contacted": req.get("dj_user_id", ""),
                "source": "demande_contact",
            })

    total = len(contacts)
    paginated = contacts[skip:skip + limit]
    return {
        "contacts": paginated,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/admin/contacts/stats")
async def admin_contacts_stats(request: Request):
    """Admin: Get segmentation statistics for contacts."""
    await require_admin(request)

    # DJ stats
    total_djs = await db.dj_profiles.count_documents({})
    active_djs = await db.dj_profiles.count_documents({"subscription_status": "active"})
    inactive_djs = total_djs - active_djs
    boosted_djs = await db.dj_profiles.count_documents({"boost_active": True})

    # Get DJs per department
    pipeline_dept = [
        {"$group": {"_id": "$department_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]
    djs_by_dept = await db.dj_profiles.aggregate(pipeline_dept).to_list(20)

    # Get DJs per region
    pipeline_region = [
        {"$group": {"_id": "$region_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    djs_by_region = await db.dj_profiles.aggregate(pipeline_region).to_list(20)

    # Client stats
    total_contacts = await db.contact_requests.count_documents({})
    unread_contacts = await db.contact_requests.count_documents({"read": False})

    # Unique client emails
    pipeline_unique = [
        {"$group": {"_id": "$client_email"}},
        {"$count": "total"},
    ]
    unique_result = await db.contact_requests.aggregate(pipeline_unique).to_list(1)
    unique_clients = unique_result[0]["total"] if unique_result else 0

    # Contacts by event type
    pipeline_events = [
        {"$match": {"type_evenement": {"$ne": ""}}},
        {"$group": {"_id": "$type_evenement", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    contacts_by_event = await db.contact_requests.aggregate(pipeline_events).to_list(20)

    return {
        "djs": {
            "total": total_djs,
            "active": active_djs,
            "inactive": inactive_djs,
            "boosted": boosted_djs,
            "by_department": [{"name": d["_id"] or "Non renseigné", "count": d["count"]} for d in djs_by_dept],
            "by_region": [{"name": r["_id"] or "Non renseigné", "count": r["count"]} for r in djs_by_region],
        },
        "clients": {
            "total_requests": total_contacts,
            "unread": unread_contacts,
            "unique_clients": unique_clients,
            "by_event_type": [{"name": e["_id"], "count": e["count"]} for e in contacts_by_event],
        },
    }


@router.get("/admin/contacts/export-csv")
async def admin_export_contacts_csv(
    request: Request,
    type: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
):
    """Admin: Export contacts as CSV for external mailing tools."""
    await require_admin(request)

    # Reuse the list logic
    result = await admin_list_contacts(
        request=request, type=type, status=status,
        department=department, search=search, page=1, limit=10000,
    )
    contacts = result["contacts"]

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    # Header
    writer.writerow([
        "Type", "Nom", "Nom de scène", "Email", "Téléphone",
        "Ville", "Code postal", "Département", "Région",
        "Statut abonnement", "Plan", "SIRET", "Assurance RC",
        "N° RC Pro", "Tarif", "Note", "Avis", "Vues",
        "Instagram", "Site web", "Date inscription", "Source",
    ])

    for c in contacts:
        created = c.get("created_at", "")
        if hasattr(created, "strftime"):
            created = created.strftime("%d/%m/%Y %H:%M")
        elif isinstance(created, str) and "T" in created:
            created = created[:10]

        writer.writerow([
            "DJ" if c["contact_type"] == "dj" else "Client",
            c.get("nom", ""),
            c.get("nom_de_scene", ""),
            c.get("email", ""),
            c.get("telephone", ""),
            c.get("ville", ""),
            c.get("code_postal", ""),
            f"{c.get('department_code', '')} - {c.get('department_name', '')}".strip(" -"),
            c.get("region_name", ""),
            c.get("subscription_status", ""),
            c.get("subscription_plan", ""),
            c.get("siret", ""),
            c.get("assurance_rc_organisme", ""),
            c.get("assurance_rc_numero", ""),
            c.get("tarif_indicatif", ""),
            c.get("note_moyenne", ""),
            c.get("nombre_avis", ""),
            c.get("nombre_vues", ""),
            c.get("instagram", ""),
            c.get("site_internet", ""),
            created,
            c.get("source", ""),
        ])

    output.seek(0)
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"contacts_djmatch_{now_str}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
