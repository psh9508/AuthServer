from typing import List
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.schemas.outbox_event import OutboxEvent as OutboxEventSchema
from src.routers.models.outbox_event import OutboxEvent as OutboxEventModel

class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    
    async def ainsert(self, outbox: OutboxEventSchema):
        stmt = insert(OutboxEventSchema).values(
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
    

    async def get_pending_events(self, limit: int = 100) -> List[OutboxEventModel]:
        stmt = select(OutboxEventSchema).where(
            OutboxEventSchema.status == 'PENDING'
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    

    async def update_status(self, event_id: int, status: str, error_message: str | None = None):
        stmt = update(OutboxEventSchema).where(
            OutboxEventSchema.id == event_id
        ).values(
            status=status,
            error_message=error_message
        )
        
        await self.session.execute(stmt)