from fastapi import APIRouter, Depends

from src.services.exceptions.user_exception import *
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
    try:
        return await auth_service.averify_user(request.user_id, request.login_id, request.verification_code)
    except VerificationCodeExpiredError:
        return {"error": "verification_code_expired", "action": "request_new_code"}
    except UserNotFoundError:
        return {"error": "user_not_found"}
    except UserAlreadyVerifiedError:
        return {"error": "user_already_verified"}

