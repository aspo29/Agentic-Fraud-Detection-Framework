import json


import json


class GeoRedisStore:

    def __init__(self, redis_client):
        self.redis = redis_client

    # -----------------------------
    # LOCATION STORAGE
    # -----------------------------
    def get_last_location(self, user_id: str):
        data = self.redis.get(f"geo:last_location:{user_id}")

        if not data:
            return None

        try:
            return json.loads(data)
        except Exception:
            return None

    def set_last_location(self, user_id: str, location: dict):
        self.redis.set(
            f"geo:last_location:{user_id}",
            json.dumps(location)
        )

    # -----------------------------
    # DEVICE STORAGE
    # -----------------------------
    def get_devices(self, user_id: str):
        data = self.redis.smembers(f"geo:devices:{user_id}")

        if data is None:
            return set()

        return set(data)

    def add_device(self, user_id: str, fingerprint: str):
        key = f"geo:devices:{user_id}"

        self.redis.sadd(key, fingerprint)
        self.redis.expire(key, 60 * 60 * 24 * 30)  # 30 days TTL