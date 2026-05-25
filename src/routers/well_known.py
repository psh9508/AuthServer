from fastapi import APIRouter

from src.core.jwt_logic import JwtLogic

router = APIRouter(tags=["well-known"])


@router.get("/.well-known/jwks.json")
async def get_jwks() -> dict:
    return JwtLogic.get_jwks()
