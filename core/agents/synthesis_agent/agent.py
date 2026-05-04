import time
from typing import List, Dict, Any
from core.agents.base.base_agent import BaseAgent
from core.agents.base.agent_result import AgentResult
from core.models.transaction_model import TransactionModel

class SynthesisAgent:
    """
    Synthesis Agent: Context-aware weighted voting. 
    The nature of the transaction determines model weights.
    High-value P2P transfers weight Graph Neural Net more; QR payments weight the Velocity Agent more.
    """
    
    def __init__(self):
        # Define baseline weights for different transaction contexts
        self.context_weights = {
            "P2P_TRANSFER": {
                "velocity_agent": 0.2,
                "geo_agent": 0.2,
                "behavior_agent": 0.2,
                "gnn_agent": 0.4  # P2P heavily weights Graph Neural Net for account linkage
            },
            "QR_PAYMENT": {
                "velocity_agent": 0.4, # QR heavily weights velocity
                "geo_agent": 0.3,
                "behavior_agent": 0.3,
                "gnn_agent": 0.0
            },
            "DEFAULT": {
                "velocity_agent": 0.33,
                "geo_agent": 0.33,
                "behavior_agent": 0.34,
                "gnn_agent": 0.0
            }
        }
        
    async def synthesize(self, transaction: TransactionModel, agent_results: List[AgentResult]) -> AgentResult:
        start_time = time.time()
        
        # Determine transaction context (mocked logic based on amount or metadata)
        # In reality, this would use metadata from TransactionModel
        context_type = "DEFAULT"
        if hasattr(transaction, "metadata") and transaction.metadata:
            context_type = transaction.metadata.get("transaction_type", "DEFAULT")
        elif transaction.amount > 50000:
            context_type = "P2P_TRANSFER"
        else:
            context_type = "QR_PAYMENT"
            
        weights = self.context_weights.get(context_type, self.context_weights["DEFAULT"])
        
        final_score = 0.0
        applied_weights = {}
        
        for result in agent_results:
            agent_name = result.agent_name
            # If an agent isn't in weights, assign a default small weight
            weight = weights.get(agent_name, 0.1) 
            final_score += result.score * weight
            applied_weights[agent_name] = weight
            
        # Normalize score to ensure it is [0, 1]
        total_weight = sum(applied_weights.values())
        if total_weight > 0:
            final_score = final_score / total_weight
            
        reason = f"Context-aware synthesis applied for {context_type}. Dominant risk factors identified."
        
        latency_ms = (time.time() - start_time) * 1000
        
        return AgentResult(
            agent_name="synthesis_agent",
            score=final_score,
            reason=reason,
            metadata={
                "context_type": context_type,
                "applied_weights": applied_weights
            },
            latency_ms=latency_ms
        )
