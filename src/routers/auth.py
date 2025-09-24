from fastapi import APIRouter, Depends

from src.factories.redis import get_redis_service
from src.services.redis_service import RedisService
from src.routers.models.user import LoginRes
from src.factories.services import get_auth_service
from src.services.auth_service import AuthService
from src.routers.models.auth import *

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/refresh_access_token')
async def refresh_access_token(request: RefreshAccessTokenReq, 
                               auth_service: AuthService = Depends(get_auth_service)
    ) -> LoginRes:
    return await auth_service.arefresh_access_token(request.access_token, request.refresh_token)


@router.post('/user_verification')
async def user_email_verification(request: EmailVerificationReq,
                                  auth_service: AuthService = Depends(get_auth_service)
    ):
    return await auth_service.averify_user(request.user_id, request.verification_code)

