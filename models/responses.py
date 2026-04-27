"""
models/responses.py — Pydantic response schemas for the OTP API.
"""
from typing import Optional
from pydantic import BaseModel, Field


class SendOTPResponse(BaseModel):
    """Response body for POST /api/v1/otp/send"""

    status: str = Field(..., description="'sent' on success.", example="sent")
    transaction_id: str = Field(..., description="Echo of the transaction ID.", example="txn-20240419-001")
    message: str = Field(
        ...,
        description="Human-readable confirmation.",
        example="OTP sent to email and SMS.",
    )


class VerifyResponse(BaseModel):
    """Response body for POST /api/v1/otp/verify"""

    status: str = Field(
        ...,
        description="'approved' if both OTPs matched, 'escalated' otherwise.",
        example="approved",
    )
    reason: Optional[str] = Field(
        None,
        description="Only present when status='escalated'. Values: 'timeout' or 'mismatch'.",
        example="mismatch",
    )


class HealthResponse(BaseModel):
    """Response body for GET /health"""

    status: str = Field(..., description="'ok' when the service is healthy.", example="ok")
    redis: str = Field(..., description="'ok' or 'unreachable'", example="ok")
    db: str = Field(..., description="'ok' or 'error'", example="ok")
