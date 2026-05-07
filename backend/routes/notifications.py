"""
Email notification system for DJ Match France
Sends trial expiry reminders: J-3, J (expiry day), J+3
Uses Gmail SMTP (free)
"""
import smtplib
import asyncio
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from database import db

logger = logging.getLogger("djmatch")

# Load email config from env
import os
from dotenv import load_dotenv
load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
APP_NAME = "DJ Match France"
APP_URL = os.getenv("APP_URL", "https://dj-directory-fr.preview.emergentagent.com")


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send an email via SMTP"""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        logger.warning("SMTP not configured (SMTP_EMAIL or SMTP_APP_PASSWORD missing)")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{APP_NAME} <{SMTP_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def build_reminder_email(dj_name: str, days_info: str, is_expired: bool) -> str:
    """Build HTML email for trial reminder"""
    if is_expired:
        header_color = "#EF4444"
        header_text = "Votre essai gratuit est termine"
        cta_text = "Activer mon abonnement"
    else:
        header_color = "#F59E0B"
        header_text = f"Votre essai gratuit expire dans {days_info}"
        cta_text = "Choisir mon abonnement"

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="margin:0; padding:0; background-color:#0B0B24; font-family:Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; margin:0 auto; background-color:#12123A; border-radius:12px; overflow:hidden;">
        <tr>
          <td style="background-color:{header_color}; padding:24px; text-align:center;">
            <h1 style="color:#fff; margin:0; font-size:22px;">🎧 {APP_NAME}</h1>
          </td>
        </tr>
        <tr>
          <td style="padding:32px 24px;">
            <h2 style="color:#fff; font-size:20px; margin:0 0 16px;">{header_text}</h2>
            <p style="color:#ccc; font-size:15px; line-height:24px;">
              Bonjour {dj_name},
            </p>
            <p style="color:#ccc; font-size:15px; line-height:24px;">
              Votre periode d'essai gratuite de 15 jours {"est maintenant expiree" if is_expired else "arrive bientot a expiration"}.
            </p>
            <p style="color:#ccc; font-size:15px; line-height:24px;">
              Pour continuer a profiter pleinement de la plateforme et garder votre profil actif,
              il vous suffit de choisir votre mode de paiement directement depuis votre espace membre 💳
            </p>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0;">
              <tr>
                <td style="background-color:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.3); border-radius:12px; padding:16px; text-align:center; width:48%;">
                  <p style="color:#8B5CF6; font-size:24px; font-weight:bold; margin:0;">8€/mois</p>
                  <p style="color:#888; font-size:13px; margin:4px 0 0;">Abonnement mensuel</p>
                </td>
                <td width="4%"></td>
                <td style="background-color:rgba(139,92,246,0.2); border:2px solid #8B5CF6; border-radius:12px; padding:16px; text-align:center; width:48%;">
                  <p style="color:#8B5CF6; font-size:11px; font-weight:bold; margin:0 0 4px;">MEILLEUR CHOIX</p>
                  <p style="color:#8B5CF6; font-size:24px; font-weight:bold; margin:0;">80€/an</p>
                  <p style="color:#888; font-size:13px; margin:4px 0 0;">Economisez 16€</p>
                </td>
              </tr>
            </table>
            <a href="{APP_URL}" style="display:block; background-color:#8B5CF6; color:#fff; text-decoration:none; text-align:center; padding:16px; border-radius:12px; font-size:16px; font-weight:bold;">
              {cta_text}
            </a>
            <p style="color:#888; font-size:13px; line-height:20px; margin-top:24px;">
              Merci encore pour votre confiance 🙏<br>
              A tres vite sur DJ Match 🎧
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 24px; border-top:1px solid #1E1E4A; text-align:center;">
            <p style="color:#666; font-size:11px; margin:0;">
              DJ Match France - DJ AS - Adrien Sebert<br>
              <a href="{APP_URL}/legal" style="color:#8B5CF6; text-decoration:none;">Mentions legales</a> |
              <a href="{APP_URL}/legal" style="color:#8B5CF6; text-decoration:none;">Se desabonner</a>
            </p>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


async def check_and_send_trial_reminders():
    """Check all trial DJs and send reminders at J-3, J, J+3"""
    now = datetime.now(timezone.utc)
    logger.info("Checking trial reminders...")

    # Find all DJs in trial
    trial_djs = await db.dj_profiles.find({
        "subscription_status": "trial",
        "trial_end": {"$exists": True}
    }).to_list(1000)

    sent_count = 0
    for dj in trial_djs:
        trial_end = dj.get("trial_end")
        if not trial_end:
            continue

        # Make timezone-aware if needed
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)

        days_until_expiry = (trial_end - now).days
        user_id = dj.get("user_id")
        dj_name = dj.get("nom_de_scene") or dj.get("prenom") or "DJ"

        # Get user email
        user = await db.users.find_one({"user_id": user_id})
        if not user or not user.get("email"):
            continue
        email = user["email"]

        # Determine which reminder to send
        reminder_type = None
        if days_until_expiry == 3:
            reminder_type = "j_minus_3"
        elif days_until_expiry == 0:
            reminder_type = "j_day"
        elif days_until_expiry == -3:
            reminder_type = "j_plus_3"

        if not reminder_type:
            continue

        # Check if already sent
        already_sent = await db.email_logs.find_one({
            "user_id": user_id,
            "reminder_type": reminder_type
        })
        if already_sent:
            continue

        # Build and send email
        is_expired = days_until_expiry <= 0
        if days_until_expiry == 3:
            days_info = "3 jours"
            subject = f"⏰ {dj_name}, votre essai DJ Match expire dans 3 jours"
        elif days_until_expiry == 0:
            days_info = "aujourd'hui"
            subject = f"⚠️ {dj_name}, votre essai DJ Match expire aujourd'hui !"
        else:
            days_info = ""
            subject = f"🔒 {dj_name}, votre profil DJ Match est desactive"

        html = build_reminder_email(dj_name, days_info, is_expired)
        success = send_email(email, subject, html)

        if success:
            # Log the email
            await db.email_logs.insert_one({
                "user_id": user_id,
                "email": email,
                "reminder_type": reminder_type,
                "subject": subject,
                "sent_at": now,
            })
            sent_count += 1

    logger.info(f"Trial reminders: {sent_count} emails sent for {len(trial_djs)} trial DJs")
    return sent_count


async def reminder_scheduler():
    """Background task: check trial reminders every 6 hours"""
    while True:
        try:
            await check_and_send_trial_reminders()
        except Exception as e:
            logger.error(f"Reminder scheduler error: {e}")
        # Wait 6 hours
        await asyncio.sleep(6 * 60 * 60)
