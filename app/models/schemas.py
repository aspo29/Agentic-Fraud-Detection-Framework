from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class FraudDecision(str, Enum):
    """Fraud decision enum."""
    APPROVE = "approve"
    DENY = "deny"
    REVIEW = "review"


class TransactionRequest(BaseModel):
    """Request model for transaction processing endpoint."""
    
    transaction_id: str = Field(..., description="Unique transaction identifier", min_length=1)
    amount: float = Field(..., description="Transaction amount", gt=0)
    merchant_id: str = Field(..., description="Merchant identifier", min_length=1)
    customer_id: str = Field(..., description="Customer identifier", min_length=1)
    merchant_category: str = Field(..., description="MCC category", min_length=1)
    country: str = Field(..., description="Country code (ISO 3166-1 alpha-2)", min_length=2, max_length=2)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Transaction timestamp")
    card_present: bool = Field(default=False, description="Whether card was physically present")
    three_d_secure: bool = Field(default=False, description="Whether 3D Secure was used")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        if v > 1_000_000:
            raise ValueError("Amount cannot exceed 1,000,000")
        return v
    
    @field_validator("country")
    @classmethod
    def validate_country(cls, v):
        if not v.isalpha():
            raise ValueError("Country must contain only letters")
        return v.upper()
    
    @model_validator(mode='after')
    def validate_model(self):
        if self.merchant_id == self.customer_id:
            raise ValueError("Merchant ID and Customer ID cannot be the same")
        return self


class AgentScore(BaseModel):
    """Agent scoring information."""
    agent_name: str
    score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    reasoning: Optional[str] = None


class TransactionResponse(BaseModel):
    """Response model for transaction processing endpoint."""
    
    transaction_id: str = Field(..., description="Original transaction ID")
    decision: FraudDecision = Field(..., description="Fraud decision")
    risk_score: float = Field(..., description="Overall risk score (0-1)", ge=0, le=1)
    agent_scores: List[AgentScore] = Field(..., description="Individual agent scores")
    latency_ms: float = Field(..., description="Processing latency in milliseconds", ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN-12345",
                "decision": "approve",
                "risk_score": 0.15,
                "agent_scores": [
                    {
                        "agent_name": "velocity_agent",
                        "score": 0.1,
                        "confidence": 0.95,
                        "reasoning": "Normal transaction velocity for customer"
                    },
                    {
                        "agent_name": "amount_agent",
                        "score": 0.2,
                        "confidence": 0.85,
                        "reasoning": "Slightly elevated amount but within historical patterns"
                    }
                ],
                "latency_ms": 245.5,
                "timestamp": "2024-04-17T10:30:00.000Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    detail: str = Field(..., description="Error message")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="Detailed field errors")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Validation error",
                "errors": [
                    {
                        "loc": ["amount"],
                        "msg": "ensure this value is greater than 0",
                        "type": "value_error.number.not_gt"
                    }
                ],
                "timestamp": "2024-04-17T10:30:00.000Z"
            }
        }
