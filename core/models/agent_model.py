
#agent output model

from dataclasses import dataclass, field
from typing import List

@dataclass
class AgentModel:
    agent_name: str
    score: float              # 0.0 → 1.0 risk contribution
    flags: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)