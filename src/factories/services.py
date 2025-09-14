from fastapi import Depends

from main_app import get_rabbitmq_client
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_session
from src.repositories.user_repository import UserRepository
from src.core.rabbitmq import RabbitMQClient
from src.services.user_service import UserService
from src.services.auth_service import AuthService


def get_user_service(
      session: AsyncSession = Depends(get_session),
      message_client: RabbitMQClient = Depends(get_rabbitmq_client)
  ) -> UserService:
      return UserService(UserRepository(session), message_client)


def get_auth_service() -> AuthService:
      return AuthService()