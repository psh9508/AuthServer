from dataclasses import dataclass
from datetime import datetime


@dataclass
class IssuedAccessToken:
    access_token: str
    expires_at: datetime | None = None
