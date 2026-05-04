'''import time
from core.agents.geo_agent.agent import GeoAgent


def test_geo_latency(redis_client):
    agent = GeoAgent(redis_client)

    payload = {
        "user_id": "u1",
        "location": {"lat": 27.7, "lon": 85.3},
        "device": {"os": "android"},
        "timestamp": 1000
    }

    start = time.time()
    import asyncio
    asyncio.run(agent.process(payload))
    end = time.time()

    assert (end - start) * 1000 < 80'''  # should run under 80ms