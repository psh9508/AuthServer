import uuid
from src.repositories.user_repository import UserRepository
from src.routers.models.user import LoginRes
from src.core.jwt_logic import JwtLogic
from src.services.redis_service import RedisService
from src.services.user_service import UserService
from src.services.exceptions.user_exception import *


class AuthService:
    def __init__(self, user_repo: UserRepository, redis_service: RedisService, user_service: UserService):
        self.user_repo = user_repo
        self.redis_service = redis_service
        self.user_service = user_service


    async def arefresh_access_token(self, access_token: str, refresh_token: str) -> LoginRes:
        refresh_result = await JwtLogic.arefresh_access_token(access_token, refresh_token)
        return LoginRes(access_token=refresh_result['access_token'],
                        refresh_token=refresh_result['refresh_token'])
    

    async def averify_user(self, user_id: uuid.UUID, email: str, verification_code: str) -> bool:
        user = await self.user_repo.aget_by_user_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found")
        
        if str(user.login_id) != email:
            raise UserNotFoundError("User email mismatch")

        if bool(user.email_verified):
            raise UserAlreadyVerifiedError("User is already verified")

        stored_verification_code = await self.redis_service.aget_email_verification_code(str(user.login_id))

        if stored_verification_code is None:
            raise VerificationCodeExpiredError("Verification code has expired")

        is_verified = stored_verification_code == verification_code

        if is_verified:
            await self._averify_user(email)
            await self.redis_service.adelete_email_verification_code(str(user.login_id))

        return is_verified


    async def aregenerate_verification_code(self, user_id: uuid.UUID, email: str) -> bool:
        user = await self.user_repo.aget_by_user_id(user_id)

        if user is None:
            raise UserNotFoundError("User not found")
        
        if str(user.login_id) != email:
            raise UserNotFoundError("User email mismatch")
        
        if bool(user.email_verified):
            raise UserAlreadyVerifiedError("User is already verified")
        
        await self.user_service.aprocess_email_verification_code(str(user.login_id))

        return True


    async def _averify_user(self, email: str):
        try:
            update_count = await self.user_repo.averify_user_email(email)
            if update_count != 1:
                raise
            
            return True
        except Exception as e:
            raise
