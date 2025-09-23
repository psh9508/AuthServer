from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.models.outbox_event import OutboxEvent

class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    
    async def ainsert(self, outbox: OutboxEvent):
        stmt = insert(OutboxEvent).values(
            service=outbox.service,
            event_type=outbox.event_type,
            payload=outbox.payload,
            status=outbox.status or 'PENDING',
            retry_count=outbox.retry_count or 0,
            last_attempt_at=outbox.last_attempt_at,
            error_message=outbox.error_message
        )

        result = await self.session.execute(stmt)
        return result.inserted_primary_key