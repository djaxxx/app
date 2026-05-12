from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid

from database import db, STRIPE_API_KEY, logger
from auth import require_dj, require_auth

router = APIRouter()

SUBSCRIPTION_PRICES = {
    "monthly": {"amount": 8.00, "days": 30, "label": "Mensuel (8\u20ac/mois)"},
    "annual": {"amount": 80.00, "days": 365, "label": "Annuel (80\u20ac/an)"}
}


@router.get("/subscription/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return [
        {"id": "monthly", "amount": 8.00, "currency": "eur", "label": "Mensuel", "description": "8\u20ac/mois", "days": 30},
        {"id": "annual", "amount": 80.00, "currency": "eur", "label": "Annuel", "description": "80\u20ac/an (\u00e9conomisez 16\u20ac)", "days": 365}
    ]


@router.post("/subscription/create-checkout")
async def create_subscription_checkout(request: Request):
    """Create a Stripe checkout session for DJ subscription"""
    user_data = await require_dj(request)
    body = await request.json()
    origin_url = body.get("origin_url", "")
    plan = body.get("plan", "monthly")
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
            amount=plan_details["amount"], currency="eur",
            success_url=success_url, cancel_url=cancel_url,
            metadata={"user_id": user_data["user_id"], "type": "dj_subscription",
                      "plan": plan, "days": str(plan_details["days"])}
        )
        session = await stripe_checkout.create_checkout_session(checkout_request)
        await db.payment_transactions.insert_one({
            "transaction_id": f"txn_{uuid.uuid4().hex[:12]}", "session_id": session.session_id,
            "user_id": user_data["user_id"], "amount": plan_details["amount"], "currency": "eur",
            "type": "subscription", "plan": plan, "days": plan_details["days"],
            "status": "pending", "payment_status": "initiated", "created_at": datetime.now(timezone.utc)
        })
        return {"checkout_url": session.url, "session_id": session.session_id, "plan": plan, "amount": plan_details["amount"]}
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la cr\u00e9ation du paiement")


@router.get("/subscription/status/{session_id}")
async def get_subscription_status(session_id: str, request: Request):
    """Check subscription payment status - uses Stripe API directly"""
    await require_auth(request)
    try:
        import stripe as stripe_lib
        stripe_lib.api_key = STRIPE_API_KEY

        # Get session status directly from Stripe
        session = stripe_lib.checkout.Session.retrieve(session_id)
        payment_status = session.payment_status
        sess_status = session.status

        # Update transaction in DB
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"status": sess_status, "payment_status": payment_status, "updated_at": datetime.now(timezone.utc)}}
        )

        if payment_status == "paid":
            transaction = await db.payment_transactions.find_one({"session_id": session_id})
            if transaction and transaction.get("status") != "completed":
                days = transaction.get("days", 30)
                subscription_end = datetime.now(timezone.utc) + timedelta(days=days)
                await db.dj_profiles.update_one(
                    {"user_id": transaction["user_id"]},
                    {"$set": {"subscription_status": "active", "subscription_end_date": subscription_end,
                              "subscription_plan": transaction.get("plan", "monthly"), "is_active": True}}
                )
                await db.payment_transactions.update_one({"session_id": session_id}, {"$set": {"status": "completed"}})
                logger.info(f"Subscription activated via status check for user {transaction['user_id']}")
            elif not transaction:
                # Fallback: activate from session metadata
                try:
                    meta = dict(session.metadata) if session.metadata else {}
                    user_id = meta.get("user_id", "")
                    plan = meta.get("plan", "monthly")
                    days = int(meta.get("days", "30"))
                    if user_id:
                        subscription_end = datetime.now(timezone.utc) + timedelta(days=days)
                        await db.dj_profiles.update_one(
                            {"user_id": user_id},
                            {"$set": {"subscription_status": "active", "subscription_end_date": subscription_end,
                                      "subscription_plan": plan, "is_active": True}}
                        )
                        logger.info(f"Subscription activated from metadata for user {user_id}")
                except Exception:
                    pass

        return {"status": sess_status, "payment_status": payment_status,
                "amount_total": session.amount_total, "currency": session.currency}
    except Exception as e:
        logger.error(f"Subscription status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de verification: {str(e)}")


@router.post("/webhook/stripe")
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
            user_id = webhook_response.metadata.get("user_id") if isinstance(webhook_response.metadata, dict) else getattr(webhook_response.metadata, 'get', lambda k, d=None: d)("user_id")
            metadata = dict(webhook_response.metadata) if hasattr(webhook_response.metadata, '__iter__') else {}
            if not user_id:
                user_id = metadata.get("user_id")
            payment_type = metadata.get("type", "dj_subscription")
            plan = metadata.get("plan", "monthly")
            days = int(metadata.get("days", "30"))
            if user_id and payment_type == "dj_boost":
                boost_start = datetime.now(timezone.utc)
                boost_end = boost_start + timedelta(days=days)
                await db.dj_profiles.update_one({"user_id": user_id}, {"$set": {
                    "boost_active": True, "boost_start": boost_start,
                    "boost_end": boost_end, "boost_plan": plan,
                }})
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {"$set": {"status": "completed", "payment_status": "paid"}}
                )
            elif user_id and payment_type == "zone_extension":
                dept_code = webhook_response.metadata.get("department_code")
                if dept_code:
                    await db.dj_profiles.update_one({"user_id": user_id}, {"$addToSet": {"departments_zones": dept_code}})
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {"$set": {"status": "completed", "payment_status": "paid"}}
                )
            elif user_id:
                subscription_end = datetime.now(timezone.utc) + timedelta(days=days)
                await db.dj_profiles.update_one({"user_id": user_id}, {"$set": {
                    "subscription_status": "active", "subscription_end_date": subscription_end,
                    "subscription_plan": plan, "is_active": True
                }})
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {"$set": {"status": "completed", "payment_status": "paid"}}
                )
        return {"received": True}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"received": True}
