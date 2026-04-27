"""
services/otp_store.py — Redis OTP storage and rate limiting.

Responsible for:
- Storing OTP hashes in Redis with TTL
- Rate limiting (max N sends per transaction/channel)
- Verifying stored OTP hashes
"""
import hashlib
import logging
from typing import Optional, Tuple

import redis

from config import settings

logger = logging.getLogger(__name__)

# Module-level Redis client (lazy-connected)
_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """Return a shared Redis client, creating it on first call."""
    global _redis_client
    if _redis_client is None:
        if settings.MOCK_REDIS:
            logger.info("Initializing MOCK Redis (fakeredis)")
            import fakeredis
            _redis_client = fakeredis.FakeRedis(decode_responses=False)
        else:
            _redis_client = redis.from_url(settings.REDIS_URL)
    return _redis_client


def set_redis_client(client: redis.Redis) -> None:
    """Override the Redis client (useful for testing with fakes)."""
    global _redis_client
    _redis_client = client


# ── Key helpers ───────────────────────────────────────────────────────────────

def _txn_key(transaction_id: str, channel: str) -> str:
    return f"otp:txn:{transaction_id}:{channel}"


def _rate_key(transaction_id: str, channel: str) -> str:
    return f"otp:send_count:{transaction_id}:{channel}"


# ── Storage ───────────────────────────────────────────────────────────────────

def store_otp(transaction_id: str, channel: str, otp_hash: str) -> None:
    """Store a hashed OTP in Redis under the transaction/channel key with TTL."""
    key = _txn_key(transaction_id, channel)
    get_redis().setex(key, settings.OTP_TTL_SECONDS, otp_hash)
    logger.debug("Stored OTP hash for txn=%s channel=%s TTL=%ds", transaction_id, channel, settings.OTP_TTL_SECONDS)


# ── Rate limiting ─────────────────────────────────────────────────────────────

def increment_send_count(transaction_id: str, channel: str) -> int:
    """Increment the send counter for a transaction/channel pair.

    Sets TTL on first increment so the counter expires with the OTP window.
    Returns the new count.
    """
    key = _rate_key(transaction_id, channel)
    count = get_redis().incr(key)
    if count == 1:
        get_redis().expire(key, settings.OTP_TTL_SECONDS)
    return int(count)


def check_rate_limit(transaction_id: str, channel: str) -> None:
    """Raise RuntimeError if the send limit has been exceeded."""
    count = increment_send_count(transaction_id, channel)
    if count > settings.OTP_RATE_LIMIT:
        logger.warning(
            "Rate limit exceeded for txn=%s channel=%s count=%d limit=%d",
            transaction_id, channel, count, settings.OTP_RATE_LIMIT,
        )
        raise RuntimeError(
            f"OTP rate limit exceeded ({settings.OTP_RATE_LIMIT} per transaction). "
            "Please wait until the current OTP expires."
        )


# ── Verification ──────────────────────────────────────────────────────────────

def verify_otp(transaction_id: str, channel: str, otp_input: str) -> Tuple[bool, Optional[str]]:
    """Verify OTP input against the stored hash.

    Returns:
        (True, None)          — OTP matches
        (False, 'expired')    — Key not found / TTL elapsed
        (False, 'mismatch')   — Key present but OTP is wrong
    """
    key = _txn_key(transaction_id, channel)
    stored = get_redis().get(key)

    if not stored:
        return False, "expired"

    input_hash = hashlib.sha256(otp_input.encode()).hexdigest()
    stored_val = stored.decode() if isinstance(stored, (bytes, bytearray)) else str(stored)

    if input_hash == stored_val:
        # Consume the OTP after successful verification
        try:
            get_redis().delete(key)
        except Exception:
            pass
        return True, None

    return False, "mismatch"
