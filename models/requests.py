"""
models/requests.py — Pydantic request schemas for the OTP API.
"""
from pydantic import BaseModel, Field, validator


class SendOTPRequest(BaseModel):
    """Request body for POST /api/v1/otp/send"""

    transaction_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Unique identifier for the transaction/auth session.",
        example="txn-20240419-001",
    )
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The user initiating the OTP request.",
        example="user-abc123",
    )
    email: str = Field(
        ...,
        description="Recipient email address for the email OTP.",
        example="user@example.com",
    )
    phone_number: str = Field(
        ...,
        description="Recipient phone number for the SMS OTP (E.164 recommended).",
        example="+9779800000000",
    )

    @validator("phone_number")
    def phone_must_have_digits(cls, v: str) -> str:
        digits = [c for c in v if c.isdigit()]
        if len(digits) < 7:
            raise ValueError("phone_number must contain at least 7 digits")
        return v


class VerifyRequest(BaseModel):
    """Request body for POST /api/v1/otp/verify"""

    transaction_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The same transaction_id used when sending the OTP.",
        example="txn-20240419-001",
    )
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The user submitting the OTP.",
        example="user-abc123",
    )
    email_otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6-digit OTP received via email.",
        example="482910",
    )
    sms_otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6-digit OTP received via SMS.",
        example="739021",
    )
    phone_number: str = Field(
        ...,
        description="Phone number for SIM-swap detection.",
        example="+9779800000000",
    )
