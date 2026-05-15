

import jwt

from core.JWT.jwt_logic import JwtLogic


class JWT_RS256(JwtLogic):
    @classmethod
    def initialize(cls, settings):
        cls.SECRET_KEY = settings.jwt.rs256.secret
        cls.REFRESH_KEY = settings.jwt.rs256.secret
        cls.AUTHSERVER_ALGORITHM = "RS256"
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
        if not cls.SECRET_KEY:
            raise RuntimeError("The JWT SECRET_KEY has not been configured")
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
        pass