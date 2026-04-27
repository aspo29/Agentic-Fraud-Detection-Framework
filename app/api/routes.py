import time
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from app.models.schemas import (
    TransactionRequest,
    TransactionResponse,
    ErrorResponse,
    AgentScore,
    FraudDecision
)
from app.middleware.auth import APIKeyMiddleware, api_key_header
from app.services.kafka_service import KafkaService
from app.services.decision_service import DecisionSynthesisService
from app.config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["transactions"])
logger = logging.getLogger(__name__)


@router.post(
    "/transaction",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        422: {
            "model": ErrorResponse,
            "description": "Validation error - invalid payload"
        },
        401: {
            "description": "Unauthorized - invalid or missing API key"
        }
    }
)
async def process_transaction(
    request: TransactionRequest,
    api_key: str = Depends(APIKeyMiddleware.verify_api_key)
) -> TransactionResponse:
    """
    Process a transaction and return fraud detection decision.
    
    **Authentication**: Requires `X-API-Key` header with valid API key
    
    **Request Body**: JSON with transaction details
    
    **Response**: Fraud decision with risk score and agent scores within 800ms (p95)
    
    **Examples**:
    
    ```json
    {
        "transaction_id": "TXN-12345",
        "amount": 150.50,
        "merchant_id": "MER-ABC123",
        "customer_id": "CUST-XYZ789",
        "merchant_category": "5411",
        "country": "US",
        "card_present": true,
        "three_d_secure": false
    }
    ```
    """
    start_time = time.time()
    
    try:
        # Log incoming request
        logger.info(
            f"Processing transaction {request.transaction_id}: "
            f"amount={request.amount}, merchant={request.merchant_id}"
        )
        
        # Prepare transaction payload
        transaction_payload = {
            "transaction_id": request.transaction_id,
            "amount": request.amount,
            "merchant_id": request.merchant_id,
            "customer_id": request.customer_id,
            "merchant_category": request.merchant_category,
            "country": request.country,
            "card_present": request.card_present,
            "three_d_secure": request.three_d_secure,
            "metadata": request.metadata or {}
        }
        
        # Publish to Kafka for agent pipeline processing
        kafka_published = await KafkaService.publish_transaction(
            request.transaction_id,
            transaction_payload
        )
        
        # Get decision (from Kafka if available, or mock for testing)
        decision_data = None
        
        if kafka_published:
            # Try to get decision from Kafka with timeout
            decision_data = await KafkaService.poll_decision(
                request.transaction_id,
                settings.KAFKA_RESPONSE_TIMEOUT_MS
            )
        
        # Fallback to mock decision if Kafka not available
        if not decision_data:
            logger.warning(
                f"Using mock decision for {request.transaction_id} "
                "(Kafka unavailable or timeout)"
            )
            decision_data = DecisionSynthesisService.generate_mock_decision(
                request.transaction_id,
                request.amount,
                request.merchant_category,
                request.card_present
            )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Validate latency requirement (p95 should be < 800ms)
        if latency_ms > settings.TRANSACTION_TIMEOUT_MS:
            logger.warning(
                f"Transaction {request.transaction_id} exceeded latency SLA: "
                f"{latency_ms:.2f}ms"
            )
        
        # Parse agent scores
        agent_scores_data = decision_data.get("agent_scores", [])
        agent_scores = []
        
        for score_data in agent_scores_data:
            agent_scores.append(
                AgentScore(
                    agent_name=score_data.get("agent_name"),
                    score=float(score_data.get("score", 0)),
                    confidence=float(score_data.get("confidence", 0)),
                    reasoning=score_data.get("reasoning")
                )
            )
        
        # Build response
        response = TransactionResponse(
            transaction_id=request.transaction_id,
            decision=decision_data.get("decision"),
            risk_score=float(decision_data.get("risk_score", 0)),
            agent_scores=agent_scores,
            latency_ms=latency_ms
        )
        
        logger.info(
            f"Transaction {request.transaction_id} processed: "
            f"decision={response.decision}, risk_score={response.risk_score:.2f}, "
            f"latency={latency_ms:.2f}ms"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing transaction {request.transaction_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/health",
    tags=["health"],
    responses={200: {"description": "Service is healthy"}}
)
async def health_check() -> dict:
    """Check API health status."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
