from fastapi import APIRouter, Depends, HTTPException

from src.services.exceptions.auth_exception import EmailVerificationFailed
from src.routers.models.base_response_model import BaseResponseModel
from src.services.exceptions.user_exception import *
from src.factories.services import get_auth_service
from src.services.auth_service import AuthService
from src.routers.models.auth import *

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/refresh_access_token')
async def refresh_access_token(request: RefreshAccessTokenReq, 
                               auth_service: AuthService = Depends(get_auth_service)
    ) -> BaseResponseModel:
    result = await auth_service.arefresh_access_token(request.access_token, request.refresh_token)
    return BaseResponseModel(data=result)


@router.post('/user_verification')
async def user_email_verification(request: EmailVerificationReq,
                                  auth_service: AuthService = Depends(get_auth_service)
    ):
    is_success = await auth_service.averify_user(request.user_id, request.login_id, request.verification_code)

    if is_success:
        return BaseResponseModel(data=EmailVerificationRes(message="User verified successfully"))
    else:
        raise EmailVerificationFailed()
    

@router.post('/regenerate_verification_code')
async def regenerate_verification_code(request: RegenerateVerificationCodeReq,
                                       auth_service: AuthService = Depends(get_auth_service)
    ):
    result = await auth_service.aregenerate_verification_code(request.user_id, request.login_id)
    return BaseResponseModel(data=result)
