from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_session
from src.repositories.outbox_repository import OutboxRepository
from src.repositories.user_repository import UserRepository
from src.services import UserService, AuthService, OutboxService


def get_outbox_service(session: AsyncSession = Depends(get_session),) -> OutboxService:
      return OutboxService(OutboxRepository(session))


def get_user_service(
      session: AsyncSession = Depends(get_session),
      outbox_service: OutboxService = Depends(get_outbox_service)
  ) -> UserService:
      return UserService(UserRepository(session), outbox_service)


def get_auth_service() -> AuthService:
      return AuthService()