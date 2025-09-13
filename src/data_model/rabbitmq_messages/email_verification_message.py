from src.data_model.rabbitmq_messages.mq_message import MQMessage

class EmailVerificationMessage(MQMessage):
    email: str
