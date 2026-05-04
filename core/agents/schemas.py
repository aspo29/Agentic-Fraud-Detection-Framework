from pydantic import BaseModel, Field
from datetime import datetime


class VelocityAgentOutput(BaseModel):
    user_id: str = Field(..., description="User identifier")
    transaction_id: str = Field(..., description="Transaction identifier")

    risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraud risk score (0 safe → 1 high risk)"
    )

    window_count: int = Field(..., description="Transactions in sliding window")
    window_seconds: int = Field(..., description="Sliding window size in seconds")

    timestamp: datetime = Field(default_factory=datetime.utcnow)