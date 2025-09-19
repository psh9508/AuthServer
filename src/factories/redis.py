from fastapi import Depends
from src.core.redis_core import get_redis_client as _get_redis_client, RedisCore
from src.services.redis_service import RedisService

def get_redis_client() -> RedisCore:
    return _get_redis_client()

def get_redis_service() -> RedisService:
      return RedisService(get_redis_client())