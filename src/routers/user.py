from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_session
from src.repositories.user_repository import UserRepository
from src.routers.schemas.user import *

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/login")
async def login(request: LoginReq, session: AsyncSession = Depends(get_session)) -> LoginRes:
    user_repo = UserRepository(session)

    user = await user_repo.get(request.login_id)
    user = user and await user_repo.login(request.login_id, request.password + str(user.salt))
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return LoginRes.model_validate(user)

@router.post('/signup')
async def signup(request: SignupReq, session: AsyncSession = Depends(get_session)):
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    user_repo = UserRepository(session)
    user = await user_repo.get(request.email)

    if user:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    
    inserted_user = await user_repo.signup(request.email, request.password)

    return LoginRes.model_validate(inserted_user)
    
