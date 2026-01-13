import uuid
from src.routers.models.user import LoginRes, LoginSuccessRes, EmailVerificationRequiredRes
from src.services.redis_service import RedisService
from src.services.outbox_service import OutboxService
from src.services.exceptions.user_exception import *
from src.repositories.schemas.user import User
from src.core.jwt_logic import JwtLogic
from src.repositories.user_repository import UserRepository
from src.constants.jwt_constants import REFRESH_TOKEN_EXPIRE


class UserService:
    def __init__(self, user_repo: UserRepository, outbox_service: OutboxService, redis_service: RedisService):
        self.user_repo = user_repo
        self.outbox_service = outbox_service
        self.redis_service = redis_service


    async def alogin(self, login_id: str, password: str) -> LoginRes:
        user = await self.user_repo.alogin(login_id, password)
        
        if not user:
            attemps_count = await self.redis_service.aadd_login_attempts_count(login_id)
            raise UserNotFoundError(login_attempts=attemps_count)
        elif not bool(user.email_verified):
            raise EmailNotVerifiedError(user_id= str(user.user_id))
        
        jwt_result = await JwtLogic.acreate_user_jwt(str(user.user_id))

        await self.redis_service.arefresh_refresh_token(
            str(user.user_id), 
            jwt_result['refresh_token'], 
            int(REFRESH_TOKEN_EXPIRE.total_seconds())
        )

        # On login success, delete the login attempts count.

        return LoginSuccessRes(
            access_token=jwt_result['access_token'], 
            refresh_token=jwt_result['refresh_token'],
        )


    async def asignup(self, email: str, password: str) -> User:
        inserted_user = await self.user_repo.asignup(email, password)
        await self.aprocess_email_verification_code(str(inserted_user.login_id))

        return inserted_user
    
    
    async def aprocess_email_verification_code(self, login_id: str):
        await self.redis_service.aset_email_verification_code(login_id)
        await self.outbox_service.ainsert_email_verification(login_id)
