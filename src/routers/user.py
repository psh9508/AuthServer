from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_model.rabbitmq_messages.email_verification_message import EmailVerificationMessage
from src.core.message_maker import MessageMaker
from src.core.database import get_session
from main_app import get_rabbitmq_client
from src.core.rabbitmq import RabbitMQClient
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
    elif not bool(user.email_verified):
        raise HTTPException(status_code=403, detail="Email not verified")
    
    return LoginRes.model_validate(user)

@router.post('/signup')
async def signup(request: SignupReq,
                 session: AsyncSession = Depends(get_session),
                 message_client: RabbitMQClient = Depends(get_rabbitmq_client)):
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    user_repo = UserRepository(session)
    user = await user_repo.get(request.email)

    if user:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    
    inserted_user = await user_repo.signup(request.email, request.password)

    # Send email verification message to the email server
    email_verification_message = MessageMaker.make_start_message(EmailVerificationMessage, 
                                                                 target='email', 
                                                                 method='verification',
                                                                 email=str(inserted_user.login_id))
    message_client.send_message(email_verification_message)

    return LoginRes.model_validate(inserted_user)
    
