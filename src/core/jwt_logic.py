from datetime import datetime, timedelta
from typing import Literal, Union
import jwt

from src.factories.redis import get_redis_service
from src.constants.jwt_constants import REFRESH_TOKEN_EXPIRE

class JwtLogic:
    SECRET_KEY: str
    REFRESH_KEY: str
    AUTHSERVER_ALGORITHM: str = "HS256"
    GITHUB_APP_ALGORITHM: str = "RS256"
    is_initialized = False

    @classmethod
    def initialize(cls, config: dict):
        cls.SECRET_KEY = config['jwt']['secret']
        cls.REFRESH_KEY = config['jwt']['refresh_secret']
        cls.is_initialized = True

    @classmethod
    async def adecode_access_token(cls, token: str) -> dict | None:
        try:
            return jwt.decode(token, cls.SECRET_KEY, [cls.AUTHSERVER_ALGORITHM])
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
    
    @classmethod
    def _encode_jwt(
        cls,
        secret: str,
        exp_sec: int,
        algorithm: Literal["HS256", "RS256"] = "HS256",
        claims: dict[str, Union[str, int]] | None = None,
    ) -> str:
        payload : dict[str, Union[str, int]] = {
            "iat": int(datetime.now().timestamp()),
            "exp": int((datetime.now() + timedelta(seconds=exp_sec)).timestamp()),
        }

        if claims:
            payload.update(claims)

        return jwt.encode(payload, secret, algorithm=algorithm)

    @classmethod
    def create_github_app_jwt(
        cls,
        app_id: str,
        private_key: str,
        expire_seconds: int = 600,
    ) -> str:
        if not app_id:
            raise ValueError("app_id is required for GitHub App JWT creation")
        if not private_key:
            raise ValueError("private_key is required for GitHub App JWT creation")

        return cls._encode_jwt(
            secret=private_key,
            exp_sec=expire_seconds,
            algorithm=cls.GITHUB_APP_ALGORITHM,
            claims={"iss": app_id},
        )
    
    @classmethod
    def _get_access_token_jwt(cls, id: str, expire_seconds: int):
        return cls._encode_jwt(
            secret=cls.SECRET_KEY,
            exp_sec=expire_seconds,
            algorithm=cls.AUTHSERVER_ALGORITHM,
            claims={"sub": id},
        )

    @classmethod
    def _get_refresh_token_jwt(cls, id: str):
        return cls._encode_jwt(
            secret=cls.REFRESH_KEY,
            exp_sec=int(REFRESH_TOKEN_EXPIRE.total_seconds()),
            algorithm=cls.AUTHSERVER_ALGORITHM,
            claims={"sub": id},
        )
    
