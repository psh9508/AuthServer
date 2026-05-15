from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Literal, Union
import jwt

from src.factories.redis import get_redis_service
from src.constants.jwt_constants import REFRESH_TOKEN_EXPIRE

class JwtLogic(ABC):
    SECRET_KEY: str
    REFRESH_KEY: str
    AUTHSERVER_ALGORITHM: str
    is_initialized = False

    @classmethod
    @abstractmethod
    def initialize(cls, settings):
        pass

    @classmethod
    @abstractmethod
    async def adecode_access_token(cls, token: str) -> dict | None:
        pass

    @classmethod
    @abstractmethod
    async def acreate_user_jwt(cls, id: str, expire_seconds: int = 1800):
        pass

    @classmethod
    @abstractmethod
    async def arefresh_access_token(cls, access_token:str, refresh_token: str):
        pass

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