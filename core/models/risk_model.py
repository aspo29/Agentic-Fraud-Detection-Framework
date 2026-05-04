# risk_model.py

# Final risk decision model after synthesizing all agent outputs

from dataclasses import dataclass, field
from typing import List, Dict, Any
from core.models.agent_model import AgentModel


@dataclass
class RiskModel:
    """
    Final fraud decision after synthesis of all agents
    """

    user_id: str
    transaction_id: str

    # Final aggregated risk score (0.0 → 1.0)
    final_risk_score: float

    # Decision outcome
    decision: str  # "ALLOW", "REVIEW", "BLOCK"

    # All agent outputs that contributed
    agent_results: List[AgentModel]

    # Human-readable explanation
    reasons: List[str] = field(default_factory=list)

    # Triggered rule names
    triggered_rules: List[str] = field(default_factory=list)

    # System metadata
    model_version: str = "v1.0"
    timestamp: int = 0