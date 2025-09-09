from pydantic import BaseModel
from datetime import datetime

class UserReq(BaseModel):
    login_id: str
    password: str

class UserRes(BaseModel):
    id: int
    login_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True