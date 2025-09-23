from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from src.factories.rebbitmq import get_message_queue_service
from src.core.database import get_session
from src.repositories.user_repository import UserRepository
from src.services.message_queue_service import MessageQueueService, get_rabbitmq_client
from src.services.user_service import UserService
from src.services.auth_service import AuthService

def get_user_service(
      session: AsyncSession = Depends(get_session),
      message_queue_service: MessageQueueService = Depends(get_message_queue_service)
  ) -> UserService:
      return UserService(UserRepository(session), message_queue_service)


def get_auth_service() -> AuthService:
      return AuthService()