import base64
from datetime import datetime, timedelta
from typing import Union
import jwt
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key, Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from src.constants.jwt_constants import REFRESH_TOKEN_EXPIRE

ALGORITHM = "RS256"


class JwtLogic:
    _private_key: str | None = None
    _public_key: str | None = None

    @classmethod
    def initialize(cls, settings):
        cls._private_key = settings.jwt.secret
        private_key_obj = load_pem_private_key(cls._private_key.encode(), password=None)
        cls._public_key = private_key_obj.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()

    @classmethod
    def get_jwks(cls) -> dict:
        if not cls._public_key:
            raise RuntimeError("JwtLogic not initialized")

        public_key_obj = load_pem_public_key(cls._public_key.encode())
        if not isinstance(public_key_obj, RSAPublicKey):
            raise ValueError("Only RSA public keys are supported")

        pub_numbers = public_key_obj.public_numbers()

        def _int_to_base64url(n: int) -> str:
            byte_len = (n.bit_length() + 7) // 8
            return base64.urlsafe_b64encode(n.to_bytes(byte_len, "big")).rstrip(b"=").decode()

        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "alg": "RS256",
                    "n": _int_to_base64url(pub_numbers.n),
                    "e": _int_to_base64url(pub_numbers.e),
                }
            ]
        }

    @classmethod
    async def acreate_user_jwt(cls, id: str, expire_seconds: int = 1800):
        if not id:
            raise ValueError("sub or user_id is required for JWT creation")

        return {
            'access_token': cls._encode_jwt(expire_seconds, {"sub": id}),
            'refresh_token': cls._encode_jwt(int(REFRESH_TOKEN_EXPIRE.total_seconds()), {"sub": id}),
        }

    @classmethod
    async def adecode_access_token(cls, token: str) -> dict | None:
        try:
            return jwt.decode(token, cls._public_key, algorithms=[ALGORITHM])
        except Exception:
            return None

    @classmethod
    async def arefresh_access_token(cls, access_token: str, refresh_token: str):
        if access_token is None or refresh_token is None:
            raise ValueError("Access token and refresh token are required")

        from src.factories.redis import get_redis_service

        try:
            user_info = jwt.decode(access_token, cls._public_key, algorithms=[ALGORITHM], options={"verify_exp": False})
        except jwt.InvalidTokenError:
            raise ValueError("Invalid access token format")

        try:
            refresh_payload = jwt.decode(refresh_token, cls._public_key, algorithms=[ALGORITHM])
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
    def _encode_jwt(cls, exp_sec: int, claims: dict[str, Union[str, int]] | None = None) -> str:
        now = datetime.now()
        payload: dict[str, Union[str, int]] = {
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=exp_sec)).timestamp()),
        }
        if claims:
            payload.update(claims)
        return jwt.encode(payload, cls._private_key, algorithm=ALGORITHM)