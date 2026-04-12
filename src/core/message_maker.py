from typing import Type, TypeVar
from src.config.settings import get_settings
from src.data_model.rabbitmq_messages.mq_message import MQMessage

T = TypeVar('T', bound=MQMessage)

class MessageMaker:
    @staticmethod
    def make_start_message(message_model: Type[T], **kwargs) -> T:
        settings = get_settings()
        return message_model(
            origin=settings.server_name,
            source=settings.server_name,
            **kwargs,
        )