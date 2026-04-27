"""
services/otp_generator.py — OTP generation and hashing.

Responsible for:
- Generating cryptographically random 6-digit OTPs
- Hashing OTPs with bcrypt (or SHA-256 fallback)
"""
import secrets
import hashlib

try:
    import bcrypt as _bcrypt
except ImportError:
    _bcrypt = None


def generate_otp() -> str:
    """Generate a random 6-digit OTP with leading zeros."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    """
    Hash the OTP for secure storage.

    Uses bcrypt when available (constant-time comparison, salted).
    Falls back to SHA-256 if bcrypt is not installed.
    """
    if _bcrypt:
        return _bcrypt.hashpw(otp.encode(), _bcrypt.gensalt()).decode()
    return hashlib.sha256(otp.encode()).hexdigest()


def sha256_hash(otp: str) -> str:
    """Return a plain SHA-256 hex digest (used for Redis transaction keys)."""
    return hashlib.sha256(otp.encode()).hexdigest()
