import asyncio
from fastapi import Depends
import pika
from pika.adapters.asyncio_connection import AsyncioConnection

from config.config import get_rabbitmq_config
from src.data_model.mq_config import MQConfig
from src.data_model.rabbitmq_messages.mq_message import MQMessage

class RabbitMQClient:    
    def __init__(self, config):
        rabbitmq_config = config['rabbitmq']
        self.host = rabbitmq_config['host']
        self.port = rabbitmq_config['port']
        self.user = rabbitmq_config['user']
        self.password = rabbitmq_config['password']
        self.vhost = rabbitmq_config['vhost']
        
        self.connected_event = asyncio.Event()
        self.loop = asyncio.get_running_loop()
        self.connection = None
        self.channel = None
        self.is_init = False
        self.exchange_name = get_rabbitmq_config().exchange_name
        self.server_name = get_rabbitmq_config().server_name


    async def ainitialize_message_queue(self):
        if not self.exchange_name:
            raise ValueError("Exchange name must be provided for initializing the message queue")

        self.connection = AsyncioConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.vhost,
                credentials=pika.PlainCredentials(self.user, self.password)
            ),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            custom_ioloop=self.loop
        )

        await self.connected_event.wait()
        if not self.is_init:
            raise RuntimeError("Failed to connect to RabbitMQ")
        

    def on_connection_open(self, connection):
        self.connection = connection
        connection.channel(on_open_callback=self.on_channel_open)


    def on_channel_open(self, channel):
        self.channel = channel
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic')
        self.channel.queue_declare(queue=self.server_name)
        self.channel.queue_bind(exchange=self.exchange_name, 
                                queue=self.server_name, 
                                routing_key=f'*.{self.server_name}.*') # {source}.{target}.{method}

        self.is_init = True
        self.connected_event.set()
        print("RabbitMQ initialized")


    def on_connection_open_error(self, _, exception):
        print(f"[Error] RabbitMQ connection failed: {exception}")
        self.is_success = False
        self.connected_event.set()

    def send_message(self, message: MQMessage):
        if not self.channel:
            raise RuntimeError("RabbitMQ channel is not initialized")        
        
        routing_key = f'{message.source}.{message.target}.{message.method}'
        self.channel.basic_publish(exchange=self.exchange_name, 
                                   routing_key=routing_key, 
                                   body=message.model_dump_json())