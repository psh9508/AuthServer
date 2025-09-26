import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, validator
from datetime import datetime

class LoginReq(BaseModel):
    user_id: uuid.UUID = Field(...)
    login_id: str = Field(...)
    password: str = Field(...)

class LoginRes(BaseModel):
    access_token: str
    refresh_token: str

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
    
    id: int
    created_at: datetime
    updated_at: datetime