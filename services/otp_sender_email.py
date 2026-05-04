"""
services/otp_sender_email.py — Email OTP delivery.

Responsible for:
- Sending OTPs via SendGrid (preferred)
- Sending OTPs via SMTP (fallback)
"""
import logging
import smtplib
from email.message import EmailMessage

import requests

from config import settings

logger = logging.getLogger(__name__)


def _send_via_sendgrid(to_email: str, otp: str) -> None:
    """Send OTP using the SendGrid v3 REST API."""
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": settings.EMAIL_FROM},
        "subject": "Your GIBL Verification Code",
        "content": [
            {
                "type": "text/plain",
                "value": (
                    f"Your GIBL verification code is: {otp}\n\n"
                    f"This code expires in 5 minutes. Do not share it with anyone."
                ),
            }
        ],
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    if resp.status_code >= 400:
        logger.error("SendGrid delivery failed: status=%s body=%s", resp.status_code, resp.text)
        raise RuntimeError(f"SendGrid delivery failed with status {resp.status_code}")
    logger.info("SendGrid accepted email to %s", to_email)


def _send_via_smtp(to_email: str, otp: str) -> None:
    """Send OTP using plain SMTP."""
    if not settings.SMTP_HOST or settings.SMTP_PORT == 0:
        raise RuntimeError("SMTP is not configured. Set SMTP_HOST and SMTP_PORT in .env")

    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = "Your GIBL Verification Code"
    msg.set_content(
        f"Your GIBL verification code is: {otp}\n\n"
        f"This code expires in 5 minutes. Do not share it with anyone."
    )

    try:
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
            server.starttls()

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.send_message(msg)
        server.quit()
        logger.info("SMTP email sent to %s", to_email)
    except Exception:
        logger.exception("SMTP delivery failed for %s", to_email)
        raise


def send_email(to_email: str, otp: str) -> None:
    """Send OTP via email — uses SendGrid if configured, otherwise SMTP.

    Raises RuntimeError if neither provider is configured or delivery fails.
    """
    if settings.SENDGRID_API_KEY:
        _send_via_sendgrid(to_email, otp)
    elif settings.SMTP_HOST:
        _send_via_smtp(to_email, otp)
    else:
        raise RuntimeError(
            "No email provider configured. "
            "Set SENDGRID_API_KEY or SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASSWORD in .env"
        )
