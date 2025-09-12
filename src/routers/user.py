from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_session
from src.repositories.user_repository import UserRepository
from src.routers.schemas.user import *

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/login")
async def login(request: UserReq, session: AsyncSession = Depends(get_session)) -> UserRes:
    user_repo = UserRepository(session)

    user = await user_repo.get(request.login_id)
    user = user and await user_repo.login(request.login_id, request.password + str(user.salt))
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return UserRes.model_validate(user)