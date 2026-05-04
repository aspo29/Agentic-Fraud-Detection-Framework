# agent_registry.py

from core.agents.velocity_agent.agent import VelocityAgent
from core.agents.geo_agent.agent import GeoAgent
# from core.agents.behavioral_agent.agent import BehavioralAgent
# from core.agents.synthesis_agent.agent import SynthesisAgent

from core.registry.dependency_map import DEPENDENCY_MAP


class AgentRegistry:

    def __init__(self):

        self._agents = {
            "velocity_agent": VelocityAgent(),
            "geo_agent": GeoAgent(),

            # "behavioral_agent": BehavioralAgent(),
            # "synthesis_agent": SynthesisAgent(),
        }

        self._dependency_map = DEPENDENCY_MAP

    def get(self, name: str):
        agent = self._agents.get(name)

        if not agent:
            raise ValueError(f"Agent '{name}' not found")

        return agent

    def get_dependencies(self, name: str):
        return self._dependency_map.get(name, {})

    def list_agents(self):
        return list(self._agents.keys())