
import asyncio
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.rabbitmq_client import RabbitMQClient
from src.core.database import get_session
from src.repositories.outbox_repository import OutboxRepository
from src.services.message_queue_service import get_rabbitmq_client

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self):
        self.INTERVAL = 0.5
        self.running = False
        self.session: Optional[AsyncSession] = None
        self.outbox_repo: Optional[OutboxRepository] = None
        self.rabbitmq_client: RabbitMQClient = get_rabbitmq_client()
   

    async def astart_worker(self):
        self.running = True
        await self._ainitialize()
        
        logger.info("Worker started")
        
        while self.running:
            try:
                await self._aprocess_outbox_events()
                await asyncio.sleep(self.INTERVAL)
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)


    async def _ainitialize(self):
        self.session = await anext(get_session())
        self.outbox_repo = OutboxRepository(self.session)
    

    async def _aprocess_outbox_events(self):
        if not self.outbox_repo:
            logger.error("Worker not properly initialized")
            return
            
        try:
            events = await self.outbox_repo.get_pending_events(limit=100)
            
            for event in events:
                try:
                    import json
                    payload_dict = json.loads(str(event.payload))
                    
                    from src.data_model.rabbitmq_messages.mq_message import MQMessage
                    mq_message = MQMessage(**payload_dict)
                    
                    self.rabbitmq_client.send_message(mq_message)
                    
                    await self.outbox_repo.update_status(
                        event_id=event.id,
                        status='SENT'
                    )
                    
                    logger.info(f"Successfully sent event {event.id}")
                    
                except Exception as e:
                    await self.outbox_repo.update_status(
                        event_id=event.id,
                        status='FAILED',
                        error_message=str(e)
                    )
                    
                    logger.error(f"Failed to send event {event.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing outbox events: {e}")
    

    async def astop_worker(self):
        self.running = False
        if self.session:
            await self.session.close()
        logger.info("Worker stopped")