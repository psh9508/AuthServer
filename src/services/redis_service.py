from src.core.redis_core import RedisCore
import secrets

class RedisService:
    def __init__(self, redis_core: RedisCore):
        self.redis_core = redis_core
    
    # async def get(self, key: str) -> Optional[Any]:
    #     return await self.redis_core.aget(key)
    
    # async def set(self, key: str, value: Any, ttl: Optional[int] = None, prefix: Optional[str] = None) -> bool:
    #     return await self.redis_core.aset(key, value, ttl, prefix)
    
    # async def delete(self, key: str, prefix: Optional[str] = None) -> bool:
    #     return await self.redis_core.adelete(key, prefix)
    
    # async def exists(self, key: str, prefix: Optional[str] = None) -> bool:
    #     return await self.redis_core.aexists(key, prefix)
    
    # async def expire(self, key: str, ttl: int, prefix: Optional[str] = None) -> bool:
    #     return await self.redis_core.aexpire(key, ttl, prefix)
    
    # async def ttl(self, key: str, prefix: Optional[str] = None) -> int:
    #     return await self.redis_core.attl(key, prefix)
    
    # async def clean_up(self, key: str, batch_size: int = 10, prefix: Optional[str] = None) -> bool:
    #     return await self.redis_core.aclean_up(key, batch_size, prefix)
    
    async def arefresh_refresh_token(self, user_id: str, refresh_token: str, ttl: int) -> bool:
        try:
            key = f'refresh:{user_id}'
            self.redis_core.set_prefix('auth')
            await self.redis_core.adelete(key)
            await self.redis_core.aset(key, refresh_token, ttl)
            return True
        except Exception as e:
            raise


    async def aget_refresh_token(self, user_id: str) -> str | None:
        try:
            key = f'refresh:{user_id}'
            self.redis_core.set_prefix('auth')
            return await self.redis_core.aget(key)
        except Exception as e:
            raise


    async def aset_email_verification_code(self, user_id: str):
        try:
            key = f'email_verification:{user_id}'
            ttl = 5 * 60 
            self.redis_core.set_prefix('email')
            verification_code = f"{secrets.randbelow(1000000):06d}"
            await self.redis_core.adelete(key)
            await self.redis_core.aset(key, str(verification_code), ttl)
        except Exception as e:
            raise


    async def aget_email_verification_code(self, user_id: str) -> str | None:
        try:
            key = f'email_verification:{user_id}'
            self.redis_core.set_prefix('email')
            verification_code = await self.redis_core.aget(key)
            return str(verification_code)
        except Exception as e:
            raise


    async def adelete_email_verification_code(self, user_id: str):
        try:
            key = f'email_verification:{user_id}'
            self.redis_core.set_prefix('email')
            await self.redis_core.adelete(key)
        except Exception as e:
            # logic is going when it has exception
            pass 
