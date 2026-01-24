from fastapi import APIRouter, Depends, HTTPException
from src.services.exceptions.user_exception import *
from src.factories.services import get_user_service
from src.services.user_service import UserService
from src.routers.models.user import *
from src.routers.models.base_response_model import BaseResponseModel
from src.core.metrics import record_login_failure

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/login")
async def login(request: LoginReq, user_service: UserService = Depends(get_user_service)) -> BaseResponseModel:
    if not request.login_id or not request.password:
        record_login_failure('invalid_request')
        raise HTTPException(status_code=400, detail="Login_id and password are required")
    
    login_res = await user_service.alogin(request.login_id, request.password)
    return BaseResponseModel(data=login_res)


@router.post('/signup')
async def signup(request: SignupReq, user_service: UserService = Depends(get_user_service)) -> BaseResponseModel:
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    inserted_user = await user_service.asignup(request.email, request.password)
    return BaseResponseModel(data=SignupRes.model_validate(inserted_user))
