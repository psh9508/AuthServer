from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, text 
from src.repositories.models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def aget(self, login_id: str) -> User | None:
        stmt = select(User).where(User.login_id == login_id)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        

    async def alogin(self, login_id: str, password: str) -> User | None:
        user = await self.aget(login_id)

        if not user:
            return None

        hashed_password = self.get_hased_password(password, str(user.salt))
        stmt = select(User).where(
            User.login_id == login_id,
            User.password == hashed_password,
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def asignup(self, email:str, password: str) -> User:
        import secrets
        salt =  secrets.token_hex(16)
        hashed_password = self.get_hased_password(password, salt)
        
        stmt = insert(User).values(
            login_id = email,
            password = hashed_password,
            salt = salt,
        ).returning(User)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_hased_password(self, password: str, salt: str):
        import hashlib
        return hashlib.sha256(password.encode() + salt.encode()).digest()