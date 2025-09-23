from src.data_model.rabbitmq_messages.email_verification_message import EmailVerificationMessage
from src.core.message_maker import MessageMaker
from src.repositories.models.outbox_event import OutboxEvent
from src.repositories.outbox_repository import OutboxRepository

class OutboxService:
    def __init__(self, outbox_repo: OutboxRepository):
        self.outbox_repo = outbox_repo


    async def ainsert_email_verification(self, email: str):
        try:
            email_verification_message = MessageMaker.make_start_message(EmailVerificationMessage, 
                                                                        target='email', 
                                                                        method='verification',
                                                                        email=email)
            
            return await self.outbox_repo.ainsert(OutboxEvent(
                service = 'email',
                event_type = 'email_verification',
                payload = email_verification_message.model_dump_json(),
            ))
        except Exception as e:
            raise RuntimeError("Failed to insert outbox event") from e