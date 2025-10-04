from fastapi import Depends
from src.core.rabbitmq_client import RabbitMQClient
from src.services.message_queue_service import MessageQueueService, get_rabbitmq_client


def get_message_queue_service(rabbitmq_core: RabbitMQClient = Depends(get_rabbitmq_client)) -> MessageQueueService:
      return MessageQueueService(rabbitmq_core)
