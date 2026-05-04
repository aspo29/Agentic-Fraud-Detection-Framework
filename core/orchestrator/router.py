from core.agents.velocity_agent.agent import VelocityAgent
from core.agents.velocity_agent.redis_store import VelocityRedisStore

from core.agents.geo_agent.agent import GeoAgent
from core.agents.geo_agent.redis_store import GeoRedisStore

from core.agents.behaviour_agent.agent import BehaviorAgent
from core.agents.synthesis_agent.agent import SynthesisAgent

from core.infrastructure.kafka.producer import KafkaEventProducer
from core.models.transaction_model import TransactionModel
import redis


class RouteEngine:

    def __init__(self):

        # INFRASTRUCTURE LAYER
        self.kafka = KafkaEventProducer()

        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            socket_timeout=0.05
        )

        # VELOCITY AGENT
        velocity_store = VelocityRedisStore(redis_client)
        self.velocity_agent = VelocityAgent(velocity_store, self.kafka)

        # GEO AGENT
        geo_store = GeoRedisStore(redis_client)
        self.geo_agent = GeoAgent(redis_client)  # Fixed GeoAgent initialization based on its __init__

        # BEHAVIOR & SYNTHESIS AGENTS
        self.behavior_agent = BehaviorAgent()
        self.synthesis_agent = SynthesisAgent()

    async def route(self, transaction: dict):

        results = {}
        # Convert dict to TransactionModel for agents that require it
        txn_model = TransactionModel(
            user_id=transaction.get("user_id", "unknown"),
            amount=float(transaction.get("amount", 0.0)),
            timestamp=int(transaction.get("timestamp", 0)),
            merchant_id=transaction.get("merchant_id", "unknown"),
            ip_address=transaction.get("ip_address", "")
        )
        if "metadata" in transaction:
            txn_model.metadata = transaction["metadata"]

        # VELOCITY SCORE
        velocity_result = self.velocity_agent.process(transaction)
        results["velocity"] = velocity_result

        # GEO SCORE
        if "location" in transaction or "ip_address" in transaction:
            geo_result = await self.geo_agent.process(transaction)
            results["geo"] = geo_result

        # BEHAVIOR SCORE
        behavior_result = await self.behavior_agent.run(txn_model)
        results["behavior"] = behavior_result

        # SYNTHESIS
        # Convert dict results to a list of AgentResult or just pass to synthesize
        agent_results = []
        if "velocity" in results and hasattr(results["velocity"], "score"):
             agent_results.append(results["velocity"])
        if "geo" in results and hasattr(results["geo"], "score"):
             agent_results.append(results["geo"])
        agent_results.append(behavior_result)

        synthesis_result = await self.synthesis_agent.synthesize(txn_model, agent_results)
        results["synthesis"] = synthesis_result

        # FINAL OUTPUT
        try:
            # Publish might expect dict
            self.kafka.publish("agent.multi.output", {"transaction_id": transaction.get("transaction_id"), "decision": "reviewed"})
        except Exception as e:
            pass # Ignore kafka error if it's not running

        return results