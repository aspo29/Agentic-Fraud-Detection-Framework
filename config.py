"""
config.py — Central configuration for GIBL OTP Service.

All environment variables are read here once. Import `settings` from this
module everywhere instead of calling os.getenv() scattered across files.
"""
import os

# Load .env file automatically if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional; env vars can be set directly in the shell


class Settings:
    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ── Database ───────────────────────────────────────────────────────────
    GIBL_DB_PATH: str = os.getenv("GIBL_DB_PATH", "gibl_app.db")

    # ── Email — SendGrid (preferred) ───────────────────────────────────────
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")

    # ── Email — SMTP fallback ──────────────────────────────────────────────
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    # ── Sender email (required) ────────────────────────────────────────────
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")

    # ── SMS — Twilio (preferred) ───────────────────────────────────────────
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "")

    # ── SMS — Sparrow (Nepal alternative) ─────────────────────────────────
    SPARROW_API_KEY: str = os.getenv("SPARROW_API_KEY", "")
    SPARROW_API_URL: str = os.getenv("SPARROW_API_URL", "https://api.sparrowsms.com/v2/sms/send")
    SPARROW_SENDER: str = os.getenv("SPARROW_SENDER", "Demo")

    # ── OTP behaviour ─────────────────────────────────────────────────────
    OTP_TTL_SECONDS: int = int(os.getenv("OTP_TTL_SECONDS", "300"))
    OTP_RATE_LIMIT: int = int(os.getenv("OTP_RATE_LIMIT", "3"))

    # ── Development / Mocking ──────────────────────────────────────────────
    MOCK_REDIS: bool = os.getenv("MOCK_REDIS", "false").lower() == "true"

    def validate(self) -> None:
        """Raise RuntimeError for any required fields that are missing."""
        if not self.EMAIL_FROM:
            raise RuntimeError(
                "EMAIL_FROM environment variable is required. "
                "Set it in your .env file or shell before starting the server."
            )


settings = Settings()
