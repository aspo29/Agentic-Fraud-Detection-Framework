"""
tests/conftest.py — Shared pytest fixtures.

Key fixtures:
  - fake_redis   : In-process Redis fake (no live server needed)
  - mock_email   : Patches email delivery so tests never hit real SMTP/SendGrid
  - mock_sms     : Patches SMS delivery so tests never call Twilio/Sparrow
  - otp_svc      : Pre-configured OTPService wired to fake Redis
"""
import hashlib
import os
import pytest

# ── Fake Redis using fakeredis (install: pip install fakeredis) ───────────────
try:
    import fakeredis
    _have_fakeredis = True
except ImportError:
    _have_fakeredis = False


@pytest.fixture(autouse=True)
def env_setup(monkeypatch, tmp_path):
    """Set required env vars and redirect SQLite to a temp file."""
    monkeypatch.setenv("EMAIL_FROM", "test@example.com")
    monkeypatch.setenv("GIBL_DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")  # overridden by fake_redis

    # Reload config so Settings picks up patched env
    import importlib
    import config as cfg_mod
    importlib.reload(cfg_mod)

    # Re-point storage module to temp DB
    import services.storage as storage_mod
    storage_mod.DB_PATH = str(tmp_path / "test.db")
    storage_mod.init_db()

    yield


@pytest.fixture()
def fake_redis():
    """Return a fakeredis server instance and wire it into otp_store."""
    if not _have_fakeredis:
        pytest.skip("fakeredis not installed — run: pip install fakeredis")

    server = fakeredis.FakeRedis(decode_responses=False)
    import services.otp_store as store_mod
    store_mod.set_redis_client(server)
    yield server
    # Reset
    store_mod.set_redis_client(None)


@pytest.fixture()
def mock_email(monkeypatch):
    """Prevent real email sends; return a list of (to, otp) calls."""
    calls = []

    def _fake_send(to_email: str, otp: str):
        calls.append((to_email, otp))

    monkeypatch.setattr("services.otp_sender_email.send_email", _fake_send)
    return calls


@pytest.fixture()
def mock_sms(monkeypatch):
    """Prevent real SMS sends; return a list of (to_number, otp) calls."""
    calls = []

    def _fake_send(to_number: str, otp: str):
        calls.append((to_number, otp))

    monkeypatch.setattr("services.otp_sender_sms.send_sms", _fake_send)
    return calls


@pytest.fixture()
def otp_svc(fake_redis):
    """OTPService wired to fake Redis — no live dependencies."""
    from services.otp_service import OTPService
    return OTPService()
