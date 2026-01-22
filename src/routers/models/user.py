import uuid
from pydantic import ConfigDict, EmailStr, Field, field_validator
from datetime import datetime
from typing import Union

from src.routers.models.base_response_model import BaseResponseData

class LoginReq(BaseResponseData):
    login_id: str = Field(...)
    password: str = Field(...)

class LoginSuccessRes(BaseResponseData):
    access_token: str = Field(...)
    refresh_token: str = Field(...)

class EmailVerificationRequiredRes(BaseResponseData):
    requires_email_verification: bool = True
    user_id: str = Field(...)
    message: str = "Email verification required"

LoginRes = Union[LoginSuccessRes, EmailVerificationRequiredRes]

class SignupReq(BaseResponseData):
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def email_max_length(cls, v):
        if len(v) > 255:
            raise ValueError('Email must be at most 255 characters')
        return v
    
class SignupRes(BaseResponseData):
    model_config = ConfigDict(from_attributes=True)    
    
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime