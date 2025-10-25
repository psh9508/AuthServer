from src.data_model.rabbitmq_messages.email_verification_message import EmailVerificationMessage
from src.core.message_maker import MessageMaker
from src.core.rabbitmq_client import RabbitMQClient

_rabbitmq_client = None

def get_rabbitmq_client() -> RabbitMQClient:
    if _rabbitmq_client is None:
        raise RuntimeError("RabbitMQ client not initialized") 

    return _rabbitmq_client

class MessageQueueService:
    def __init__(self, rabbitmq_core: RabbitMQClient):
        self.core = rabbitmq_core

    @staticmethod
    async def ainitialize_rabbitmq(config):
        global _rabbitmq_client
        _rabbitmq_client = RabbitMQClient(config)
        await _rabbitmq_client.ainitialize_message_queue()

    
    async def asend_email_verification(self, email: str):
        email_verification_message = MessageMaker.make_start_message(EmailVerificationMessage, 
                                                                    target='email', 
                                                                    method='verification',
                                                                    email=email)
        await self.core.send_message(email_verification_message)
