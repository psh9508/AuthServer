import json
import redis.asyncio as redis
from typing import Any, Optional
from config.config import get_config

class RedisCore:
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self.prefix = ''

    def set_prefix(self, prefix: str):
        self.prefix = prefix
    
    def _append_prefix(self, key: str) -> str:  
        return f"{self.prefix}:{key}"    
    
    async def ainitialize(self, config) -> redis.Redis:
        redis_config = config['db']['redis']
        host = redis_config['host']
        port = redis_config.get('port', 6379)
        db = redis_config.get('db', 0)
        redis_url = f"redis://{host}:{port}"
        
        self._client = redis.Redis.from_url(
            redis_url,
            db=db,
            decode_responses=True,
        )

        self.prefix = redis_config['prefix']
        return self._client
    
    async def aget_client(self) -> redis.Redis:
        if self._client is None:
            config = get_config()
            return await self.ainitialize(config)

        return self._client
    
    async def aclose(self):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def aget(self, key: str) -> Optional[Any]:
        try:
            client = await self.aget_client()
            prefixed_key = self._append_prefix(key)
            value = await client.get(prefixed_key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    async def aset(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            client = await self.aget_client()

            prefixed_key = self._append_prefix(key)
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if ttl:
                return await client.setex(prefixed_key, ttl, value)
            else:
                return await client.set(prefixed_key, value)
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False

    async def aclean_up(self, key: str, batch_size: int = 10) -> bool:
        try:
            client = await self.aget_client()
            pattern = self._append_prefix(f"{key}:*")
            deleted_count = 0
            cursor = 0
            
            while True:
                cursor, keys = await client.scan(cursor, match=pattern, count=batch_size)
                if keys:
                    deleted_count += await client.delete(*keys)
                if cursor == 0:
                    break
                    
            return deleted_count > 0
        except Exception as e:
            print(f"Redis SAFE DELETE USER KEYS error: {e}")
            return False
        
    async def adelete(self, key: str) -> bool:
        try:
            if key is None:
                raise ValueError("key is required for deletion")

            client = await self.aget_client()
            prefixed_key = self._append_prefix(f'{key}')
            result = await client.delete(prefixed_key)
            return result > 0
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
        
    async def aexists(self, key: str) -> bool:
        try:
            client = await self.aget_client()
            prefixed_key = self._append_prefix(key)
            return await client.exists(prefixed_key) > 0
        except Exception as e:
            print(f"Redis EXISTS error: {e}")
            return False
    
    async def aexpire(self, key: str, ttl: int) -> bool:
        try:
            client = await self.aget_client()
            prefixed_key = self._append_prefix(key)
            return await client.expire(prefixed_key, ttl)
        except Exception as e:
            print(f"Redis EXPIRE error: {e}")
            return False
    
    async def attl(self, key: str) -> int:
        try:
            client = await self.aget_client()
            prefixed_key = self._append_prefix(key)
            return await client.ttl(prefixed_key)
        except Exception as e:
            print(f"Redis TTL error: {e}")
            return -2
        
    async def aincr(self, key: str, amount: int = 1) -> int:
        try:
            client = await self.aget_client()
            prefixed_key = self._append_prefix(key)
            return await client.incr(prefixed_key, amount)
        except Exception as e:
            print(f"Redis INCR error: {e}")
            return -1
        
    async def aget_pipe(self):
        try:
            client = await self.aget_client()
            return client.pipeline()
        except Exception as e:
            print(f"Redis PIPE error: {e}")
            raise


_redis_client = RedisCore()

async def ainitialize_redis(config):
    try:
        redis = await _redis_client.ainitialize(config)
        await redis.ping()
    except Exception as e:
        raise RuntimeError("Failed to initialize Redis") from e

def get_redis_client() -> RedisCore:
    return _redis_client
