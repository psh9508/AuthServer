from datetime import datetime, timedelta
from typing import Union
import jwt
from src.core.redis_client import redis_client
from src.repositories.models.user import User

class JwtLogic:
    SECRET_KEY: str | None = None
    REFRESH_KEY: str | None = None
    ALGORITHM: str = "HS256"
    is_initialized = False

    @classmethod
    def initialize(cls, config: dict):
        cls.SECRET_KEY = config['jwt']['secret']
        cls.REFRESH_KEY = config['jwt']['refresh_secret']
        cls.is_initialized = True

    @classmethod
    async def acreate_user_jwt(cls, user_info: User, expire_seconds: int = 1800):
        if not cls.is_initialized:
            raise RuntimeError("JwtLogic has not been initialized")
        if not cls.SECRET_KEY or not cls.REFRESH_KEY:
            raise RuntimeError("The JWT SECRET_KEY or REFRESH_KEY has not been configured")

        if user_info.id is None:
            raise ValueError("sub or user_id is required for JWT creation")
        
        access_token = cls._get_jwt(cls.SECRET_KEY, str(user_info.id), expire_seconds)
        
        refresh_token_expire = timedelta(weeks=1) 
        refresh_token = cls._get_jwt(cls.REFRESH_KEY, str(user_info.id), int(refresh_token_expire.total_seconds()))

        redis_refresh_token_key = f'refresh:{user_info.id}'
        await redis_client.adelete(redis_refresh_token_key)
        await redis_client.aset(redis_refresh_token_key, refresh_token, int(refresh_token_expire.total_seconds()))

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
    
    
    @classmethod
    def _get_jwt(cls, secret: str, sub: str, exp_sec: int) -> str:
        payload : dict[str, Union[str, int]] = {
            "sub": sub,
            "iat": int(datetime.now().timestamp()),
            "exp": int((datetime.now() + timedelta(seconds=exp_sec)).timestamp()),
        }

        return jwt.encode(payload, secret, cls.ALGORITHM)