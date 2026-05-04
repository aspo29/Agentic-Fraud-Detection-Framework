-- KEYS[1] = velocity:{user_id}
-- ARGV[1] = current timestamp
-- ARGV[2] = window size (seconds)

local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local window_start = now - window

-- add event
redis.call("ZADD", key, now, now)

-- remove old events
redis.call("ZREMRANGEBYSCORE", key, 0, window_start)

-- count active events
local count = redis.call("ZCARD", key)

-- keep key alive only for window duration
redis.call("EXPIRE", key, window)

return count