"""
api/server.py — FastAPI application factory.

Responsibilities:
  - Create the FastAPI app with metadata
  - Load and validate config on startup
  - Initialize the SQLite database
  - Include all routers
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from config import settings
from services import storage
from api.routes import otp, health

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Startup/Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate required env vars — fail fast rather than at first request
    settings.validate()

    # Ensure SQLite tables exist
    storage.init_db()

    logger.info("GIBL OTP Service started — DB=%s  Redis=%s", settings.GIBL_DB_PATH, settings.REDIS_URL)
    yield
    logger.info("GIBL OTP Service shutting down")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="GIBL OTP Verification Service",
    description=(
        "Dual-channel (Email + SMS) OTP verification microservice for "
        "Global IME Bank Limited, with SIM-swap fraud detection and "
        "account-escalation for failed verifications."
    ),
    version="1.0.0",
    contact={"name": "GIBL Engineering"},
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(otp.router)

if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8001, reload=True)
