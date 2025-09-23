from pydantic import BaseModel


class RefreshAccessTokenReq(BaseModel):
    access_token: str
    refresh_token: str