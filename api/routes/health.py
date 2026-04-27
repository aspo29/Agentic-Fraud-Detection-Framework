"""
api/routes/health.py — Health-check endpoint.

GET /health
  Checks Redis connectivity and SQLite DB availability.
  Returns 200 with status details even when sub-systems are degraded,
  so load balancers can distinguish "app alive" from "dependencies OK".
"""
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.responses import HealthResponse
from services.otp_store import get_redis
from services import storage

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns connectivity status for Redis and the SQLite database.",
)
def health_check():
    redis_status = "ok"
    db_status = "ok"

    # Ping Redis
    try:
        get_redis().ping()
    except Exception as exc:
        logger.warning("Redis health-check failed: %s", exc)
        redis_status = "unreachable"

    # Ping SQLite (cheap — just try fetching flagged accounts)
    try:
        storage.get_flagged_accounts()
    except Exception as exc:
        logger.warning("DB health-check failed: %s", exc)
        db_status = "error"

    overall = "ok" if redis_status == "ok" and db_status == "ok" else "degraded"
    status_code = 200 if overall == "ok" else 503

    body = HealthResponse(status=overall, redis=redis_status, db=db_status)
    return JSONResponse(content=body.dict(), status_code=status_code)
