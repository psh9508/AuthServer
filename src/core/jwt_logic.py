from datetime import datetime, timedelta
from typing import Union
import jwt
from src.core.redis_client import redis_client
from src.repositories.models.user import User

class JwtLogic:
    SECRET_KEY: str
    REFRESH_KEY: str
    ALGORITHM: str = "HS256"
    is_initialized = False

    @classmethod
    def initialize(cls, config: dict):
        cls.SECRET_KEY = config['jwt']['secret']
        cls.REFRESH_KEY = config['jwt']['refresh_secret']
        cls.is_initialized = True
        cls.refresh_token_expire = timedelta(weeks=1)

    @classmethod
    async def adecode_access_token(cls, token: str) -> dict | None:
        try:
            return jwt.decode(token, cls.SECRET_KEY, [cls.ALGORITHM])
        except Exception:
            # Expired or tampered token
            return None
        
    @classmethod
    async def acreate_user_jwt(cls, id: str, expire_seconds: int = 1800):
        if not cls.is_initialized:
            raise RuntimeError("JwtLogic has not been initialized")
        if not cls.SECRET_KEY or not cls.REFRESH_KEY:
            raise RuntimeError("The JWT SECRET_KEY or REFRESH_KEY has not been configured")
        if not id:
            raise ValueError("sub or user_id is required for JWT creation")
        
        access_token = cls._get_access_token_jwt(id, expire_seconds)
        refresh_token = cls._get_refresh_token_jwt(id)

        redis_refresh_token_key = f'refresh:{id}'
        await redis_client.adelete(redis_refresh_token_key)
        await redis_client.aset(redis_refresh_token_key, refresh_token, int(cls.refresh_token_expire.total_seconds()))

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

    @classmethod
    async def arefresh_access_token(cls, access_token:str, refresh_token: str):
        if access_token is None or refresh_token is None:
            raise ValueError("Access token and refresh token are required")
        
        try:
            user_info = jwt.decode(access_token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM], options={"verify_exp": False})
        except jwt.InvalidTokenError:
            raise ValueError("Invalid access token format")
        
        try:
            refresh_payload = jwt.decode(refresh_token, cls.REFRESH_KEY, algorithms=[cls.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid refresh token format")
        
        if user_info['sub'] != refresh_payload['sub']:
          raise PermissionError("Token user ID mismatch")
        
        refresh_token_key = cls._get_redis_refresh_token_key(user_info['sub'])
        stored_refresh_token = await redis_client.aget(refresh_token_key)

        if not stored_refresh_token:
            raise RuntimeError("Refresh token not found or expired")
        
        if refresh_token != stored_refresh_token:
            raise PermissionError("Invalid refresh token")
        
        return await cls.acreate_user_jwt(user_info['sub'])
    
    @classmethod
    def _get_jwt(cls, secret: str, sub: str, exp_sec: int) -> str:
        payload : dict[str, Union[str, int]] = {
            "sub": sub,
            "iat": int(datetime.now().timestamp()),
            "exp": int((datetime.now() + timedelta(seconds=exp_sec)).timestamp()),
        }

        return jwt.encode(payload, secret, cls.ALGORITHM)
    
    @classmethod
    def _get_access_token_jwt(cls, id: str, expire_seconds: int):
        return cls._get_jwt(cls.SECRET_KEY, id, expire_seconds)

    @classmethod
    def _get_refresh_token_jwt(cls, id: str):
        return cls._get_jwt(cls.REFRESH_KEY, id, int(cls.refresh_token_expire.total_seconds()))
    
    @classmethod
    def _get_redis_refresh_token_key(cls, id: str) -> str:
        return f'refresh:{id}'
