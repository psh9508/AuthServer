from pydantic import BaseModel

class UserReq(BaseModel):
    login_id: str
    password: str

class UserRes(BaseModel):
    id: int
    login_id: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True