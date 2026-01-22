import uuid
from pydantic import Field

from src.routers.models.base_response_model import BaseResponseData


class RefreshAccessTokenReq(BaseResponseData):
    access_token: str = Field(...)
    refresh_token: str = Field(...)

class EmailVerificationReq(BaseResponseData):
    user_id: uuid.UUID = Field(...)
    login_id: str = Field(...)    
    verification_code: str = Field(..., pattern=r'^\d{6}$')

class EmailVerificationRes(BaseResponseData):
    pass

class RegenerateVerificationCodeReq(BaseResponseData):
    user_id: uuid.UUID = Field(...)
    login_id: str = Field(...)

class RegenerateVerificationCodeRes(BaseResponseData):
    pass