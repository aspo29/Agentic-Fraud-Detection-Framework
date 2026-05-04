import time
import logging
from datetime import datetime, timezone

from core.agents.base.base_agent import BaseAgent
from core.agents.schemas import VelocityAgentOutput
from .rules import VelocityRules

logger = logging.getLogger(__name__)


class VelocityAgent(BaseAgent):
    """
    Velocity fraud detection agent:
    - Uses Redis sliding window (Lua)
    - Applies rule-based scoring
    - Publishes result to Kafka
    """

    def __init__(self, redis_store, kafka_producer):
        self.redis_store = redis_store
        self.kafka = kafka_producer


    def score(self, transaction: dict) -> float:
        user_id = transaction["user_id"]

        try:
            window_count = self.redis_store.get_window_count(user_id)
        except Exception as e:
            logger.warning(f"Redis failure fallback: {e}")
            return 0.3

        return VelocityRules.compute_score(window_count)


    def process(self, transaction: dict):
        start = time.time()

        user_id = transaction["user_id"]
        tx_id = transaction["transaction_id"]

        try:
            window_count = self.redis_store.get_window_count(user_id)
            risk_score = VelocityRules.compute_score(window_count)
       
        except Exception as e:
            logger.warning(f"Error occurred while processing transaction: {e}")
            result = VelocityAgentOutput(
                user_id=user_id,
                transaction_id=tx_id,
                risk_score=0.3,
                window_count=0,
                window_seconds=self.redis_store.window_seconds,
                timestamp=datetime.now(timezone.utc)
            )

        # publish to Kafka
        self.kafka.send("agent.velocity", result.model_dump())

        latency = (time.time() - start) * 1000
        if latency > 50:
            logger.warning(f"VelocityAgent slow: {latency:.2f}ms")

        return result
    def run(self, transaction: dict):
        """
        Standard entry point required by BaseAgent.
        """
        return self.process(transaction)