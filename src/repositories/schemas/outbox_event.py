from sqlalchemy import (
    Column, Integer, String, DateTime, Text, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class EventStatus(enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default=EventStatus.PENDING.value
    )
    retry_count = Column(Integer, nullable=False, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    sent_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<OutboxEvent(id={self.id}, type={self.event_type}, status={self.status})>"
