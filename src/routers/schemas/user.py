from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, validator
from datetime import datetime

class LoginReq(BaseModel):
    login_id: str
    password: str

class LoginRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    login_id: EmailStr
    created_at: datetime
    updated_at: datetime

    @field_validator('login_id')
    @classmethod
    def email_max_length(cls, v):
        if len(v) > 255:
            raise ValueError('login_id must be at most 255 characters')
        return v

class SignupReq(BaseModel):
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def email_max_length(cls, v):
        if len(v) > 255:
            raise ValueError('Email must be at most 255 characters')
        return v