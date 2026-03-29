import uuid
from pydantic import BaseModel, Field

from src.routers.models.base_response_model import BaseResponseData


class RefreshAccessTokenReq(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)

class EmailVerificationReq(BaseModel):
    user_id: uuid.UUID = Field(...)
    login_id: str = Field(...)    
    verification_code: str = Field(..., pattern=r'^\d{6}$')

class EmailVerificationRes(BaseResponseData):
    pass

class RegenerateVerificationCodeReq(BaseModel):
    user_id: uuid.UUID = Field(...)
    login_id: str = Field(...)

class RegenerateVerificationCodeRes(BaseResponseData):
    pass
