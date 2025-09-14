from src.routers.schemas.user import LoginRes
from src.core.jwt_logic import JwtLogic


class AuthService:
    async def arefresh_access_token(self, access_token: str, refresh_token: str) -> LoginRes:
        refresh_result = await JwtLogic.arefresh_access_token(access_token, refresh_token)
        return LoginRes(access_token=refresh_result['access_token'],
                        refresh_token=refresh_result['refresh_token'])
