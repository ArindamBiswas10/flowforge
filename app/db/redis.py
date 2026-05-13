import os
import json
import redis.asyncio as aioredis

_redis = None


async def connect_redis():
    global _redis
    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    _redis = aioredis.from_url(url, decode_responses=True)


async def close_redis():
    if _redis:
        await _redis.aclose()


async def get_redis():
    if _redis is None:
        raise RuntimeError("Redis connected nahi hai.")
    return _redis


async def publish_event(run_id: str, payload: dict):
    r = await get_redis()
    data = json.dumps(payload)
    await r.publish(f"run:{run_id}", data)
    await r.rpush(f"run:events:{run_id}", data)
    await r.expire(f"run:events:{run_id}", 300)  # 5 min tak store


async def subscribe_run(run_id: str):
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(f"run:{run_id}")
    return pubsub