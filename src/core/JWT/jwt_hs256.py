

import jwt

from AuthServer.src.core.JWT.jwt_logic import JwtLogic
from AuthServer.src.factories.redis import get_redis_service


class JWT_HS256(JwtLogic):
    
    @classmethod
    def initialize(cls, settings):
        cls.SECRET_KEY = settings.jwt.hs256.secret
        cls.REFRESH_KEY = settings.jwt.hs256.refresh_secret
        cls.AUTHSERVER_ALGORITHM = "HS256"
        cls.is_initialized = True


    @classmethod
    async def adecode_access_token(cls, token: str) -> dict | None:
        try:
            return jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.AUTHSERVER_ALGORITHM])
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
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
    

    @classmethod
    async def arefresh_access_token(cls, access_token:str, refresh_token: str):
        if access_token is None or refresh_token is None:
            raise ValueError("Access token and refresh token are required")
        
        try:
            user_info = jwt.decode(access_token, cls.SECRET_KEY, algorithms=[cls.AUTHSERVER_ALGORITHM], options={"verify_exp": False})
        except jwt.InvalidTokenError:
            raise ValueError("Invalid access token format")
        
        try:
            refresh_payload = jwt.decode(refresh_token, cls.REFRESH_KEY, algorithms=[cls.AUTHSERVER_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid refresh token format")
        
        if user_info['sub'] != refresh_payload['sub']:
          raise PermissionError("Token user ID mismatch")
        
        redis_service = get_redis_service()
        stored_refresh_token = await redis_service.aget_refresh_token(user_info['sub'])

        if not stored_refresh_token:
            raise RuntimeError("Refresh token not found or expired")
        
        if refresh_token != stored_refresh_token:
            raise PermissionError("Invalid refresh token")
        
        return await cls.acreate_user_jwt(user_info['sub'])
    