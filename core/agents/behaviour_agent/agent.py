import time
import random
from typing import Optional
from core.agents.base.base_agent import BaseAgent
from core.agents.base.agent_result import AgentResult
from core.models.transaction_model import TransactionModel

class BehaviorAgent(BaseAgent):
    """
    Behavior Agent: LSTM model trained on user's personal transaction history.
    Scores how 'normal' a new transaction looks against the personal baseline.
    """
    
    def __init__(self):
        # Mock LSTM initialization
        self.model_loaded = True
        
    async def run(self, transaction: TransactionModel, context=None) -> AgentResult:
        start_time = time.time()
        
        # In a real implementation, we would extract historical sequence features
        # from a fast storage (like Redis) and pass them through a PyTorch LSTM model.
        
        # Simulating cold-start detection
        # New users without history fall back to a cohort-based baseline
        is_cold_start = random.choice([True, False])
        
        # Mock LSTM anomaly score where [0.0 = completely normal, 1.0 = highly anomalous]
        score = random.uniform(0.05, 0.95)
        
        if score > 0.75:
            reason = "High deviation from historical behavior pattern (Time/Amount/Merchant Category)."
        elif score > 0.4:
            reason = "Slight deviation from normal behavioral sequence."
        else:
            reason = "Transaction matches user's typical behavior baseline."
            
        latency_ms = (time.time() - start_time) * 1000
        
        return AgentResult(
            agent_name="behavior_agent",
            score=score,
            reason=reason,
            metadata={
                "is_cold_start": is_cold_start,
                "model_used": "LSTM_sequence_v2",
                "cohort_fallback": "urban_retail" if is_cold_start else None
            },
            latency_ms=latency_ms
        )
