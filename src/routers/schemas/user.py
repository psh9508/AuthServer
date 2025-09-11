from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserReq(BaseModel):
    login_id: str
    password: str

class UserRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    login_id: str
    created_at: datetime
    updated_at: datetime