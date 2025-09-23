from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


class OutboxEvent(BaseModel):
    id : int
    service: str = Field(..., max_length=100)
    event_type: str = Field(..., max_length=100)
    payload: dict
    status: Literal['PENDING', 'SENT', 'FAILED'] = 'PENDING'
    retry_count: int = 0
    last_attempt_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    sent_at: datetime | None = None

    class Config:
        orm_mode = True