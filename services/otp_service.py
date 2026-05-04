"""
services/otp_service.py — OTP orchestration facade.

This module is the single public entry point for OTP operations.
It delegates to the focused sub-modules:
  - otp_generator  : generate & hash
  - otp_store      : Redis storage, rate limiting, verification
  - otp_sender_email : email delivery
  - otp_sender_sms   : SMS delivery

Keeping this facade means existing callers don't need to change.
"""
import logging
import time
from typing import Optional, Tuple

from services.otp_generator import generate_otp, sha256_hash
from services.otp_store import store_otp, check_rate_limit, verify_otp as _verify_otp
from services import otp_sender_email, otp_sender_sms

logger = logging.getLogger(__name__)


class OTPService:
    """Facade that coordinates OTP generation, storage, delivery and verification."""

    # ── Email OTP ──────────────────────────────────────────────────────────

    def send_email_otp(
        self,
        transaction_id: str,
        to_email: str,
        otp: Optional[str] = None,
    ) -> str:
        """Generate, store, and deliver an OTP to the given email address.

        Args:
            transaction_id: Unique identifier for this auth transaction.
            to_email:       Recipient email address.
            otp:            Override OTP value (useful for testing).

        Returns:
            The plaintext OTP (for transactional use / logging).
        """
        start = time.time()
        otp = otp or generate_otp()

        check_rate_limit(transaction_id, "email")

        otp_hash = sha256_hash(otp)
        store_otp(transaction_id, "email", otp_hash)

        otp_sender_email.send_email(to_email, otp)

        logger.info("Email OTP sent for txn=%s to=%s in %.2fs", transaction_id, to_email, time.time() - start)
        return otp

    # ── SMS OTP ────────────────────────────────────────────────────────────

    def send_sms_otp(
        self,
        transaction_id: str,
        phone_number: str,
        otp: Optional[str] = None,
    ) -> str:
        """Generate, store, and deliver an OTP to the given phone number via SMS.

        Args:
            transaction_id: Unique identifier for this auth transaction.
            phone_number:   Recipient phone number (E.164 format recommended).
            otp:            Override OTP value (useful for testing).

        Returns:
            The plaintext OTP.
        """
        start = time.time()
        otp = otp or generate_otp()

        check_rate_limit(transaction_id, "sms")

        otp_hash = sha256_hash(otp)
        store_otp(transaction_id, "sms", otp_hash)

        otp_sender_sms.send_sms(phone_number, otp)

        logger.info("SMS OTP sent for txn=%s to=%s in %.2fs", transaction_id, phone_number, time.time() - start)
        return otp

    # ── Verification ───────────────────────────────────────────────────────

    def verify_otp(
        self,
        transaction_id: str,
        channel: str,
        otp_input: str,
    ) -> Tuple[bool, Optional[str]]:
        """Verify an OTP submitted by the user.

        Returns:
            (True, None)          — OTP is valid
            (False, 'expired')    — OTP has expired or was never stored
            (False, 'mismatch')   — OTP present but does not match
        """
        return _verify_otp(transaction_id, channel, otp_input)

    # ── Legacy helpers (kept for backwards-compatibility with tests) ────────

    def _generate_otp(self) -> str:
        return generate_otp()

    def store_otp(self, transaction_id: str, channel: str, otp_hash: str) -> None:
        store_otp(transaction_id, channel, otp_hash)

    # Legacy send_sms kept for backwards compat with existing tests
    def send_sms(
        self,
        phone_number: str,
        otp: Optional[str] = None,
        transaction_id: Optional[str] = None,
        channel: str = "sms",
    ) -> str:
        txn = transaction_id or phone_number
        return self.send_sms_otp(txn, phone_number, otp=otp)

    # Legacy send_email kept for backwards compat with existing tests
    def send_email(self, user_email: str, otp: Optional[str] = None) -> str:
        txn = f"email:{user_email}"
        return self.send_email_otp(txn, user_email, otp=otp)
