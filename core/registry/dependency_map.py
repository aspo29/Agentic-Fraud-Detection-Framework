# dependency_map.py


DEPENDENCY_MAP = {
    "velocity_agent": {
        "kafka_topics": [
            "transactions.raw",
            "agent.velocity"
        ],
        "stores": ["redis_velocity_store"],
        "requires": ["kafka_producer", "redis_client"]
    },

    "geo_agent": {
        "kafka_topics": [
            "transactions.raw",
            "agent.geo"
        ],
        "stores": ["redis_geo_store"],
        "requires": ["kafka_producer", "redis_client", "geoip_service"]
    },

    "behavioral_agent": {
        "kafka_topics": [
            "transactions.raw",
            "agent.behavioral"
        ],
        "stores": ["redis_behavior_store"],
        "requires": ["kafka_producer", "redis_client", "behavior_model"]
    },

    "synthesis_agent": {
        "kafka_topics": [
            "agent.velocity",
            "agent.geo",
            "agent.behavioral",
            "agent.synthesis"
        ],
        "stores": ["redis_synthesis_store"],
        "requires": ["kafka_consumer", "kafka_producer", "risk_aggregator"]
    }
}