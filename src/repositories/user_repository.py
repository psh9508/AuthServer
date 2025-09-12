from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from src.repositories.models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, login_id: str) -> Optional[User]:
        stmt = select(User).where(User.login_id == login_id)
        
        result = result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        

    async def login(self, login_id: str, password: str) -> Optional[User]:
        stmt = select(User).where(
            User.login_id == login_id,
            User.password == text("digest(:password, 'sha256')")
        ).params(password=password)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()