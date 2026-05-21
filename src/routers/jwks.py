import base64

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from fastapi import APIRouter, HTTPException

from src.core.jwt_logic import JwtLogic

router = APIRouter()


def _int_to_base64url(n: int) -> str:
    length = (n.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()


@router.get("/.well-known/jwks.json", tags=["jwks"])
async def jwks():
    if JwtLogic._public_key is None:
        raise HTTPException(status_code=503, detail="Public key not initialized")

    pub_numbers = load_pem_public_key(JwtLogic._public_key.encode()).public_numbers()

    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": JwtLogic._kms_key_id,
                "n": _int_to_base64url(pub_numbers.n),
                "e": _int_to_base64url(pub_numbers.e),
            }
        ]
    }
