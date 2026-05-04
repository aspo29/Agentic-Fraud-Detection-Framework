"""
services/otp_sender_sms.py — SMS OTP delivery.

Responsible for:
- Sending OTPs via Twilio (preferred)
- Sending OTPs via Sparrow SMS (Nepal alternative)
"""
import logging
import time

import requests

from config import settings

logger = logging.getLogger(__name__)


def _send_via_twilio(to_number: str, body: str) -> dict:
    """Send SMS using the Twilio REST API."""
    acct = settings.TWILIO_ACCOUNT_SID
    token = settings.TWILIO_AUTH_TOKEN
    from_num = settings.TWILIO_FROM_NUMBER

    if not (acct and token and from_num):
        raise RuntimeError(
            "Twilio credentials not fully configured. "
            "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER in .env"
        )

    url = f"https://api.twilio.com/2010-04-01/Accounts/{acct}/Messages.json"
    data = {"From": from_num, "To": to_number, "Body": body}
    resp = requests.post(url, data=data, auth=(acct, token), timeout=20)
    return {"status_code": resp.status_code, "text": resp.text, "timestamp": time.time()}


def _send_via_sparrow(to_number: str, body: str) -> dict:
    """Send SMS using the Sparrow SMS REST API (Nepal)."""
    api_key = settings.SPARROW_API_KEY
    api_url = settings.SPARROW_API_URL
    sender = settings.SPARROW_SENDER

    if not (api_key and api_url and sender):
        raise RuntimeError(
            "Sparrow SMS credentials not fully configured. "
            "Set SPARROW_API_KEY, SPARROW_API_URL, and SPARROW_SENDER in .env"
        )

    payload = {"sender": sender, "to": to_number, "message": body}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(api_url, json=payload, headers=headers, timeout=20)
    return {"status_code": resp.status_code, "text": resp.text, "timestamp": time.time()}


def send_sms(to_number: str, otp: str) -> None:
    """Send OTP via SMS — uses Twilio if configured, otherwise Sparrow.

    Raises RuntimeError if neither provider is configured or delivery fails.
    """
    body = f"Your GIBL verification code is: {otp}. Expires in 5 minutes. Do not share."

    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        result = _send_via_twilio(to_number, body)
        provider = "Twilio"
    elif settings.SPARROW_API_KEY:
        result = _send_via_sparrow(to_number, body)
        provider = "Sparrow"
    else:
        raise RuntimeError(
            "No SMS provider configured. "
            "Set Twilio or Sparrow credentials in .env"
        )

    status_code = result.get("status_code", 500)
    ok = 200 <= status_code < 300 or status_code == 201
    status_label = "ok" if ok else "failed"
    logger.info(
        "SMS delivery via %s: to=%s status=%s ts=%s resp=%s",
        provider, to_number, status_label, result.get("timestamp"), result.get("text"),
    )

    if not ok:
        raise RuntimeError(f"{provider} SMS delivery failed: status={status_code} body={result.get('text')}")
