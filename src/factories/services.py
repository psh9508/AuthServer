from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from src.factories.redis import get_redis_service
from src.core.database import get_session
from src.repositories.outbox_repository import OutboxRepository
from src.repositories.user_repository import UserRepository
from src.services.redis_service import RedisService
from src.services import UserService, AuthService, OutboxService


def get_outbox_service(session: AsyncSession = Depends(get_session),) -> OutboxService:
      return OutboxService(OutboxRepository(session))


def get_user_service(
      session: AsyncSession = Depends(get_session),
      outbox_service: OutboxService = Depends(get_outbox_service),
      redis_service: RedisService = Depends(get_redis_service)
  ) -> UserService:
      return UserService(UserRepository(session), outbox_service, redis_service)


def get_auth_service(session: AsyncSession = Depends(get_session),
                     redis_service: RedisService = Depends(get_redis_service)
  ) -> AuthService:
      return AuthService(UserRepository(session), redis_service)