from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from src.factories.redis import get_redis_service
from src.core.database import get_session
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.redis_service import RedisService
from src.services.user_service import UserService


def get_user_service(
      session: AsyncSession = Depends(get_session),
      redis_service: RedisService = Depends(get_redis_service)
  ) -> UserService:
      return UserService(session, redis_service)


def get_auth_service(session: AsyncSession = Depends(get_session),
                     redis_service: RedisService = Depends(get_redis_service),
                     user_service: UserService = Depends(get_user_service)
  ) -> AuthService:
      return AuthService(UserRepository(session), redis_service, user_service)
