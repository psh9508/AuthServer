from src.routers.schemas.user import LoginRes
from src.services.outbox_service import OutboxService
from src.services.exceptions.user_exception import *
from src.services.message_queue_service import MessageQueueService
from src.repositories.models.user import User
from src.core.jwt_logic import JwtLogic
from src.repositories.user_repository import UserRepository
from src.data_model.rabbitmq_messages.email_verification_message import EmailVerificationMessage


class UserService:
    def __init__(self, user_repo: UserRepository, outbox_service: OutboxService):
        self.user_repo = user_repo
        self.outbox_service = outbox_service


    async def alogin(self, login_id: str, password: str) -> LoginRes:
        user = await self.user_repo.alogin(login_id, password)
        
        if not user:
            raise UserNotFoundError("Invalid credentials")
        elif not bool(user.email_verified):
            raise EmailNotVerifiedError("Email not verified")
        
        jwt_result = await JwtLogic.acreate_user_jwt(str(user.id))
        return LoginRes(access_token=jwt_result['access_token'], 
                        refresh_token=jwt_result['refresh_token'])


    async def asignup(self, email: str, password: str) -> User:
        user = await self.user_repo.aget(email)

        if user:
            raise DuplicateEmailError("Uasend_email_verificationser with this email already exists")

        inserted_user = await self.user_repo.asignup(email, password)
        await self.outbox_service.ainsert_email_verification(str(inserted_user.login_id))

        return inserted_user