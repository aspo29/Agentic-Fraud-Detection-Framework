import logging
import random
from typing import Dict, List, Any
from app.models.schemas import AgentScore, FraudDecision

logger = logging.getLogger(__name__)


class DecisionSynthesisService:
    """Service for synthesizing fraud decisions from agent scores."""
    
    @staticmethod
    def generate_mock_decision(
        transaction_id: str,
        amount: float,
        merchant_category: str,
        card_present: bool
    ) -> Dict[str, Any]:
        """Generate mock agent scores and decision for testing.
        
        Args:
            transaction_id: Transaction ID
            amount: Transaction amount
            merchant_category: MCC category
            card_present: Whether card was present
            
        Returns:
            Dict with decision and agent scores
        """
        # Mock agent scores
        velocity_score = 0.1 + random.uniform(-0.05, 0.15)  # Lower is better
        amount_score = min(0.3, amount / 50000)  # Higher amounts = higher risk
        merchant_score = 0.05 if card_present else 0.15
        location_score = random.uniform(0.0, 0.2)
        network_score = 0.1 + random.uniform(-0.05, 0.1)
        
        agent_scores = [
            AgentScore(
                agent_name="velocity_agent",
                score=min(1.0, velocity_score),
                confidence=0.85 + random.uniform(0, 0.15),
                reasoning="Analyzed transaction frequency and volume patterns"
            ),
            AgentScore(
                agent_name="amount_agent",
                score=min(1.0, amount_score),
                confidence=0.90 + random.uniform(0, 0.1),
                reasoning="Evaluated transaction amount against customer history"
            ),
            AgentScore(
                agent_name="merchant_agent",
                score=min(1.0, merchant_score),
                confidence=0.80 + random.uniform(0, 0.2),
                reasoning="Checked merchant reputation and category"
            ),
            AgentScore(
                agent_name="location_agent",
                score=min(1.0, location_score),
                confidence=0.75 + random.uniform(0, 0.25),
                reasoning="Analyzed geographic consistency"
            ),
            AgentScore(
                agent_name="network_agent",
                score=min(1.0, network_score),
                confidence=0.85 + random.uniform(0, 0.15),
                reasoning="Cross-referenced with known fraud patterns"
            ),
        ]
        
        # Calculate overall risk score
        overall_risk = sum(score.score * 0.2 for score in agent_scores)
        
        # Make decision based on risk score
        if overall_risk < 0.3:
            decision = FraudDecision.APPROVE
        elif overall_risk < 0.6:
            decision = FraudDecision.REVIEW
        else:
            decision = FraudDecision.DENY
        
        logger.info(
            f"Generated decision for {transaction_id}: {decision} "
            f"(risk_score={overall_risk:.2f})"
        )
        
        return {
            "transaction_id": transaction_id,
            "decision": decision.value,
            "risk_score": min(1.0, overall_risk),
            "agent_scores": [score.dict() for score in agent_scores]
        }
