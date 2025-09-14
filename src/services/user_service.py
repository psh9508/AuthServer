from src.routers.schemas.user import LoginRes
from src.services.exceptions.user_exception import *
from src.repositories.models.user import User
from src.core.jwt_logic import JwtLogic
from src.core.message_maker import MessageMaker
from src.core.rabbitmq import RabbitMQClient
from src.repositories.user_repository import UserRepository
from src.data_model.rabbitmq_messages.email_verification_message import EmailVerificationMessage


class UserService:
    def __init__(self, user_repo: UserRepository, message_client: RabbitMQClient):
        self.user_repo = user_repo
        self.message_client = message_client


    async def alogin(self, login_id: str, password: str) -> LoginRes:
        user = await self.user_repo.alogin(login_id, password)
        
        if not user:
            raise UserNotFoundError("Invalid credentials")
        elif not bool(user.email_verified):
            raise EmailNotVerifiedError("Email not verified")
        
        jwt = JwtLogic.create_user_jwt(user)
        return LoginRes(access_token=jwt)


    async def asignup(self, email: str, password: str) -> User:
        user = await self.user_repo.aget(email)

        if user:
            raise DuplicateEmailError("User with this email already exists")
        
        inserted_user = await self.user_repo.asignup(email, password)

        # Send email verification message to the email server
        email_verification_message = MessageMaker.make_start_message(EmailVerificationMessage, 
                                                                    target='email', 
                                                                    method='verification',
                                                                    email=str(inserted_user.login_id))
        self.message_client.send_message(email_verification_message)

        return inserted_user