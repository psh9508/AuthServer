from typing import Type, TypeVar
from config.config import get_rabbitmq_config
from src.data_model.rabbitmq_messages.mq_message import MQMessage

T = TypeVar('T', bound=MQMessage)

class MessageMaker:
    @staticmethod
    def make_start_message(message_model: Type[T], **kwargs) -> T:
        mq_config = get_rabbitmq_config()
        return message_model(
            origin=mq_config.server_name,
            source=mq_config.server_name,
            **kwargs,
        )