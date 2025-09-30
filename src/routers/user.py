from fastapi import APIRouter, Depends, HTTPException
from src.services.exceptions.user_exception import *
from src.factories.services import get_user_service
from src.services.user_service import UserService
from src.routers.models.user import *

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/login")
async def login(request: LoginReq, user_service: UserService = Depends(get_user_service)) -> LoginRes:
    if not request.login_id or not request.password:
        raise HTTPException(status_code=400, detail="Login_id and password are required")
    
    try:
        login_res = await user_service.alogin(request.login_id, request.password)
        return login_res
    except UserNotFoundError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except EmailNotVerifiedError:
        raise HTTPException(status_code=403, detail="Email not verified")


@router.post('/signup')
async def signup(request: SignupReq, user_service: UserService = Depends(get_user_service)) -> SignupRes:
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        inserted_user = await user_service.asignup(request.email, request.password)
        return SignupRes.model_validate(inserted_user)
    except DuplicateEmailError:
        raise HTTPException(status_code=409, detail="User with this email already exists")
        
