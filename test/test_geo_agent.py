import asyncio
from core.agents.geo_agent.agent import GeoAgent


class FakeRedis:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

    def smembers(self, key):
        return self.data.get(key, set())

    def sadd(self, key, value):
        self.data.setdefault(key, set()).add(value)

    def expire(self, key, ttl):
        pass


def test_kathmandu_to_dharan_impossible_travel():

    redis_client = FakeRedis()
    agent = GeoAgent(redis_client)

    user_id = "u1"

    kathmandu = {
        "user_id": user_id,
        "location": {"lat": 27.7172, "lon": 85.3240},
        "device": {
            "user_agent": "chrome",
            "os": "android",
            "screen": "1080",
            "ip": "1.1.1.1"
        },
        "timestamp": 1000
    }

    dharan = {
        "user_id": user_id,
        "location": {"lat": 26.8120, "lon": 87.2833},
        "device": {
            "user_agent": "chrome",
            "os": "android",
            "screen": "1080",
            "ip": "1.1.1.1"
        },
        "timestamp": 1000 + 1200  # 20 minutes later
    }

    async def run():
        await agent.process(kathmandu)
        return await agent.process(dharan)

    result = asyncio.run(run())

    assert "impossible_travel" in result["flags"]
    