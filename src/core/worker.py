
import asyncio
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.rabbitmq_client import RabbitMQClient
from src.core.database import get_session
from src.repositories.outbox_repository import OutboxRepository
from src.repositories.schemas.outbox_event import EventStatus
from src.services.message_queue_service import get_rabbitmq_client

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self):
        self.INTERVAL = 0.5
        self.running = False
        self.outbox_repo: Optional[OutboxRepository] = None
        self.rabbitmq_client: RabbitMQClient = get_rabbitmq_client()

        self.rabbitmq_client.subscribe_delivery_confirmation(self.handle_delivery_confirmation)
   
    
    async def astart_worker(self):
        self.running = True
        logger.info("Worker started")

        async for session in get_session():
            self.outbox_repo = OutboxRepository(session)
            
            while self.running:
                try:
                    await self._aprocess_outbox_events()
                    await session.commit()
                    await asyncio.sleep(self.INTERVAL)
                except Exception as e:
                    logger.error(f"Worker error: {e}")
                    await session.rollback()
                    await asyncio.sleep(1)
            
            logger.info("Worker stopped")
            break


    async def _aprocess_outbox_events(self):
        if not self.outbox_repo:
            logger.error("Worker not properly initialized")
            return
            
        try:
            events = await self.outbox_repo.get_processable_events()
                
            for event in events:
                try:
                    import json
                    payload_dict = json.loads(str(event.payload))
                    
                    from src.data_model.rabbitmq_messages.mq_message import MQMessage
                    mq_message = MQMessage(**payload_dict)
                    
                    await self.rabbitmq_client.send_message(mq_message, event.id)
                except Exception as e:
                    await self.outbox_repo.update_status(
                        event_id=event.id,
                        status=EventStatus.FAILED.value,
                        error_message=str(e)
                    )
                    
                    logger.error(f"Failed to send event {event.id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error processing outbox events: {e}")
            raise


    async def handle_delivery_confirmation(self, event_data):
        if not self.outbox_repo:
            return

        type = event_data['type']
        event_id = event_data['event_id']

        status_map = {
            "ack": {
                "status": EventStatus.SENT.value,
                "sent_at": datetime.now(),
                "error_message": None,
            },
            "nack": {
                "status": EventStatus.FAILED.value,
                "sent_at": None,
            }
        }

        values = status_map.get(type)
        
        if not values:
            return

        await self.outbox_repo.update_status(event_id=event_id, **values)
        

    async def astop_worker(self):
        self.running = False
        self.rabbitmq_client.unsubscribe_delivery_confirmation(self.handle_delivery_confirmation)