from src.core.redis_client import redis_client, RedisClient

async def get_redis_client() -> RedisClient:
    return redis_client