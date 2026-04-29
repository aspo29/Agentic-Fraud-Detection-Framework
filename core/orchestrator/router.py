from core.agents.velocity_agent.agent import VelocityAgent
from core.agents.velocity_agent.redis_store import VelocityRedisStore

from core.agents.geo_agent.agent import GeoAgent
from core.agents.geo_agent.redis_store import GeoRedisStore

from core.infrastructure.kafka.producer import KafkaEventProducer
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
        self.geo_agent = GeoAgent(geo_store, self.kafka)  # GeoAgent internally builds store


        # FUTURE AGENTS (PLACEHOLDERS)

        # self.behavioral_agent = BehavioralAgent(...)
        # self.synthesis_agent = SynthesisAgent(...)

    async def route(self, transaction: dict):

        results = {}
        # VELOCITY SCORE

        velocity_result = self.velocity_agent.process(transaction)
        results["velocity"] = velocity_result

        # GEO SCORE (if location exists)

        if "location" in transaction:
            geo_result = await self.geo_agent.process(transaction)
            results["geo"] = geo_result


        # FUTURE EXTENSIONS

        # behavioral_result = self.behavioral_agent.process(transaction)
        # results["behavioral"] = behavioral_result

        # synthesis_result = self.synthesis_agent.process(results)
        # results["final"] = synthesis_result

        # FINAL OUTPUT (OPTIONAL)

        self.kafka.publish("agent.multi.output", results)

        return results