"""
api/routes/otp.py — OTP send and verify endpoints.

POST /api/v1/otp/send    — Generate and deliver OTP via email + SMS
POST /api/v1/otp/verify  — Verify submitted OTPs and handle SIM-swap detection
"""
import logging

from fastapi import APIRouter, HTTPException

from models.requests import SendOTPRequest, VerifyRequest
from models.responses import SendOTPResponse, VerifyResponse
from services.otp_service import OTPService
from services import carrier, storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/otp", tags=["otp"])

# Single shared service instance (stateless — safe to share)
_otp = OTPService()


# ── Send ──────────────────────────────────────────────────────────────────────

@router.post(
    "/send",
    response_model=SendOTPResponse,
    status_code=200,
    summary="Send OTP via email and SMS",
    description=(
        "Generates a 6-digit OTP for the transaction, stores its hash in Redis "
        "with a 5-minute TTL, and delivers it via email (SendGrid/SMTP) and "
        "SMS (Twilio/Sparrow). Rate-limited to 3 sends per transaction."
    ),
)
def send_otp(req: SendOTPRequest):
    txn = req.transaction_id

    errors = []

    # Send email OTP
    try:
        _otp.send_email_otp(txn, req.email)
    except Exception as exc:
        logger.error("Email OTP send failed for txn=%s: %s", txn, exc)
        errors.append(f"email: {str(exc)}")

    # Send SMS OTP
    try:
        _otp.send_sms_otp(txn, req.phone_number)
    except Exception as exc:
        logger.error("SMS OTP send failed for txn=%s: %s", txn, exc)
        errors.append(f"sms: {str(exc)}")

    if errors:
        # Both channels failed — surface as 502
        raise HTTPException(status_code=502, detail={"errors": errors})

    logger.info("OTP dispatched for txn=%s user=%s", txn, req.user_id)
    return SendOTPResponse(
        status="sent",
        transaction_id=txn,
        message="OTP sent to email and SMS.",
    )


# ── Verify ────────────────────────────────────────────────────────────────────

@router.post(
    "/verify",
    response_model=VerifyResponse,
    status_code=200,
    summary="Verify OTP (email + SMS dual-channel)",
    description=(
        "Verifies both email and SMS OTPs for the transaction. "
        "If the phone number was SIM-swapped within 48 hours, SMS-only "
        "authentication is blocked and email OTP is mandatory. "
        "Failed verifications flag the account for manual review."
    ),
)
def verify_otp(req: VerifyRequest):
    txn = req.transaction_id
    user_id = req.user_id

    # SIM-swap heuristic: if ported within 48 h, enforce email requirement
    ported = carrier.was_ported_within(req.phone_number, hours=48)
    if ported:
        logger.warning(
            "SIM-swap detected for phone=%s txn=%s — enforcing dual-channel",
            req.phone_number, txn,
        )

    # Verify both channels
    email_ok, email_reason = _otp.verify_otp(txn, "email", req.email_otp)
    sms_ok, sms_reason = _otp.verify_otp(txn, "sms", req.sms_otp)

    # If recently ported: SMS alone is not sufficient
    if ported and sms_ok and not email_ok:
        sms_ok = False
        sms_reason = "sim_swap_policy"

    if email_ok and sms_ok:
        logger.info("OTP approved for txn=%s user=%s", txn, user_id)
        return VerifyResponse(status="approved")

    # Determine escalation reason: expired > mismatch
    reason = "timeout" if "expired" in (email_reason, sms_reason) else "mismatch"

    storage.flag_account(user_id, txn, reason)
    logger.warning("OTP escalated for txn=%s user=%s reason=%s", txn, user_id, reason)
    return VerifyResponse(status="escalated", reason=reason)
