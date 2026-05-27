import asyncio
import base64
import json
from datetime import datetime, timedelta
from typing import Union

import boto3
import jwt
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_der_public_key
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from src.constants.jwt_constants import REFRESH_TOKEN_EXPIRE

ALGORITHM = "RS256"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


class JwtLogic:
    _public_key: str | None = None
    _kms_client = None
    _kms_key_id: str | None = None

    @classmethod
    def initialize(cls, settings):
        cls._kms_key_id = settings.jwt.kms_key_id
        cls._kms_client = boto3.client("kms", region_name=settings.jwt.region)

        response = cls._kms_client.get_public_key(KeyId=cls._kms_key_id)
        cls._public_key = load_der_public_key(response["PublicKey"]).public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        ).decode()

    @classmethod
    def get_jwks(cls) -> dict:
        if not cls._public_key:
            raise RuntimeError("JwtLogic not initialized")

        from cryptography.hazmat.primitives.serialization import load_pem_public_key
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

        loop = asyncio.get_event_loop()
        access_token, refresh_token = await asyncio.gather(
            loop.run_in_executor(None, cls._encode_jwt, expire_seconds, {"sub": id}),
            loop.run_in_executor(None, cls._encode_jwt, int(REFRESH_TOKEN_EXPIRE.total_seconds()), {"sub": id}),
        )
        return {'access_token': access_token, 'refresh_token': refresh_token}

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

        header_b64 = _b64url(json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode())
        payload_b64 = _b64url(json.dumps(payload, separators=(",", ":")).encode())
        signing_input = f"{header_b64}.{payload_b64}".encode()

        response = cls._kms_client.sign(
            KeyId=cls._kms_key_id,
            Message=signing_input,
            MessageType="RAW",
            SigningAlgorithm="RSASSA_PKCS1_V1_5_SHA_256",
        )
        return f"{header_b64}.{payload_b64}.{_b64url(response['Signature'])}"
