import uuid
from pydantic import Field

from src.routers.models.base_response_model import BaseResonseData


class RefreshAccessTokenReq(BaseResonseData):
    access_token: str = Field(...)
    refresh_token: str = Field(...)

class EmailVerificationReq(BaseResonseData):
    user_id: uuid.UUID = Field(...)
    login_id: str = Field(...)    
    verification_code: str = Field(..., pattern=r'^\d{6}$')

class EmailVerificationRes(BaseResonseData):
    pass

class RegenerateVerificationCodeReq(BaseResonseData):
    user_id: uuid.UUID = Field(...)
    login_id: str = Field(...)

class RegenerateVerificationCodeRes(BaseResonseData):
    pass