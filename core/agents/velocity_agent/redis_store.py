import time

class VelocityRedisStore:
    """
    Redis ZSET-based sliding window store using Lua script.
    """

    def __init__(self, redis_client, window_seconds=120):
        self.redis = redis_client
        self.window_seconds = window_seconds
        self.lua_sha = None

        if self.lua_sha is None:
            with open("core/agents/velocity_agent/lua_scripts/velocity.lua") as f:
                self.lua_sha = self.redis.script_load(f.read())

    def get_window_count(self, user_id: str) -> int:
        key = f"velocity:{user_id}"
        now = int(time.time())

        try:
            result = self.redis.evalsha(
                self.lua_sha,
                1,
                key,
                now,
                self.window_seconds
            )
            return int(result)

        except Exception:
            return 0  # safe fallback