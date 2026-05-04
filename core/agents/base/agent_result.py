from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AgentResult:
    agent_name: str
    score: float  # MUST be [0,1]
    reason: str
    metadata: Dict[str, Any]
    latency_ms: float