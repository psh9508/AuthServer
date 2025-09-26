import uuid
from pydantic import BaseModel, Field


class RefreshAccessTokenReq(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)

class EmailVerificationReq(BaseModel):
    user_id: uuid.UUID = Field(...)
    login_id: str = Field(...)    
    verification_code: str = Field(..., pattern=r'^\d{6}$')

class RegenerateVerificationCode(BaseModel):
    user_id: uuid.UUID = Field(...)
    login_id: str = Field(...)