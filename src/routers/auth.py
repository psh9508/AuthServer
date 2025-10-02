from fastapi import APIRouter, Depends, HTTPException

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
        is_success = await auth_service.averify_user(request.user_id, request.login_id, request.verification_code)

        if is_success:
            return {"success": True, "message": "User verified successfully"}
        else:
            raise HTTPException(status_code=400, detail={"error": "invalid_verification_code"})
    except VerificationCodeExpiredError:
        raise HTTPException(status_code=400, detail={"error": "verification_code_expired", "action": "request_new_code"})
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail={"error": "user_not_found"})
    except UserAlreadyVerifiedError:
        raise HTTPException(status_code=409, detail={"error": "user_already_verified"})
    

@router.post('/regenerate_verification_code')
async def regenerate_verification_code(request: RegenerateVerificationCode,
                                       auth_service: AuthService = Depends(get_auth_service)                                       
    ):
    try:
        await auth_service.aregenerate_verification_code(request.user_id, request.login_id)
        return {"success": True, "message": "Verification code regenerated"}
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail={"error": "user_not_found"})
    except UserAlreadyVerifiedError:
        raise HTTPException(status_code=409, detail={"error": "user_already_verified"})

