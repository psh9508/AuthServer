import asyncio
import time
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.models.user import LoginRes, LoginSuccessRes, EmailVerificationRequiredRes
from src.services.redis_service import RedisService
from src.services.outbox_service import OutboxService
from src.services.exceptions.user_exception import *
from src.repositories.schemas.user import User
from src.core.jwt_logic import JwtLogic
from src.repositories.user_repository import UserRepository
from src.constants.jwt_constants import REFRESH_TOKEN_EXPIRE
from src.core.metrics import login_duration, record_login_success, record_login_failure


class UserService:
    def __init__(self, session: AsyncSession, redis_service: RedisService):
        self.user_repo = UserRepository(session)
        self.outbox_service = OutboxService(session)
        self.redis_service = redis_service


    async def alogin(self, login_id: str, password: str) -> LoginRes:
        start_time = time.perf_counter() 
        status_label = 'failure'

        try:
            user = await self.user_repo.alogin(login_id, password)
            
            if not user:
                record_login_failure('invalid_credentials')
                attemps_count = await self.redis_service.aadd_login_attempts_count(login_id)
                raise InvalidCredentialsError(login_attempts=attemps_count)
            elif not bool(user.email_verified):
                record_login_failure('email_not_verified')
                raise EmailNotVerifiedError(user_id=str(user.user_id))

            asyncio.create_task(self.redis_service.adelete_login_attempts_count(login_id))        
            
            jwt_result = await JwtLogic.acreate_user_jwt(str(user.user_id))

            await self.redis_service.arefresh_refresh_token(
                str(user.user_id), 
                jwt_result['refresh_token'], 
                int(REFRESH_TOKEN_EXPIRE.total_seconds())
            )

            record_login_success()
            status_label = 'success'
            
            return LoginSuccessRes(
                access_token=jwt_result['access_token'], 
                refresh_token=jwt_result['refresh_token'],
            )        
        except Exception:
            record_login_failure('internal_server_error')
            raise
        finally:
            duration = time.perf_counter() - start_time
            login_duration.labels(status=status_label).observe(duration)


    async def asignup(self, email: str, password: str) -> User:
        inserted_user = await self.user_repo.asignup(email, password)
        await self.aprocess_email_verification_code(str(inserted_user.login_id))

        return inserted_user
    
    
    async def aprocess_email_verification_code(self, login_id: str):
        await self.redis_service.aset_email_verification_code(login_id)
        await self.outbox_service.ainsert_email_verification(login_id)
