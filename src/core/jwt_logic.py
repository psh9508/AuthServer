from datetime import datetime, timedelta
from typing import Union
import jwt
from config.config import get_config
from src.repositories.models.user import User

class JwtLogic:
    SECRET_KEY: str | None = None
    ALGORITHM: str = "HS256"
    is_initialized = False

    @classmethod
    def initialize(cls, config: dict):
        cls.SECRET_KEY = config['jwt']['secret']
        cls.is_initialized = True

    @classmethod
    def create_user_jwt(cls, user_info: User, expire_minutes: int = 30):
        if not cls.is_initialized:
            raise RuntimeError("JwtLogic has not been initialized")
        if not cls.SECRET_KEY:
            raise RuntimeError("JWT SECRET_KEY is not configured")

        if user_info.id is None:
            raise ValueError("sub or user_id is required for JWT creation")
            
        payload: dict[str, Union[str, int]] = {
            "sub": str(user_info.id),
            "iat": int(datetime.now().timestamp()),
            "exp": int((datetime.now() + timedelta(minutes=expire_minutes)).timestamp()),
        }

        return jwt.encode(payload, cls.SECRET_KEY, cls.ALGORITHM)