import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, validator
from datetime import datetime
from typing import Union

class LoginReq(BaseModel):
    login_id: str = Field(...)
    password: str = Field(...)

class LoginSuccessRes(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)

class EmailVerificationRequiredRes(BaseModel):
    requires_email_verification: bool = True
    user_id: str = Field(...)
    message: str = "Email verification required"

LoginRes = Union[LoginSuccessRes, EmailVerificationRequiredRes]

class SignupReq(BaseModel):
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def email_max_length(cls, v):
        if len(v) > 255:
            raise ValueError('Email must be at most 255 characters')
        return v
    
class SignupRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)    
    
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime