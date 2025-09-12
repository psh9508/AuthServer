from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LoginReq(BaseModel):
    login_id: str
    password: str

class LoginRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    login_id: str
    created_at: datetime
    updated_at: datetime

class SignupReq(BaseModel):
    email: str
    password: str