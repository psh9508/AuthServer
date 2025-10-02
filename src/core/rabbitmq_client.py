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
        
        self.next_seq = 0
        self.publish_lock = asyncio.Lock()
        self.connected_event = asyncio.Event()
        self.loop = asyncio.get_running_loop()
        self.connection = None
        self.channel = None
        self.is_init = False
        self.exchange_name = get_rabbitmq_config().exchange_name
        self.server_name = get_rabbitmq_config().server_name
        self.outstanding = {}  # seq: (message, event_id)
        self.delivery_subscribers = []
    
    def subscribe_delivery_confirmation(self, callback):
        self.delivery_subscribers.append(callback)
    
    def unsubscribe_delivery_confirmation(self, callback):
        if callback in self.delivery_subscribers:
            self.delivery_subscribers.remove(callback)
    
    async def _notify_delivery_confirmation(self, event_data):
        for callback in self.delivery_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_data)
                else:
                    callback(event_data)
            except Exception as e:
                print(f"Error in delivery confirmation callback: {e}") 


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
        self.next_seq = 0
        self.outstanding.clear()

        self.channel.confirm_delivery(self.on_delivery_confirmation)
        self.channel.add_on_return_callback(self.on_returned_message)

        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic')
        self.channel.queue_declare(queue=self.server_name)
        self.channel.queue_bind(exchange=self.exchange_name, 
                                queue=self.server_name, 
                                routing_key=f'*.{self.server_name}.*') # {source}.{target}.{method}

        self.is_init = True
        self.connected_event.set()


    def on_connection_open_error(self, _, exception):
        print(f"[Error] RabbitMQ connection failed: {exception}")
        self.is_success = False
        self.connected_event.set()


    async def send_message(self, message: MQMessage, event_id: int | None = None):
        if not self.channel:
            raise RuntimeError("RabbitMQ channel is not initialized")        
        
        routing_key = f'{message.source}.{message.target}.{message.method}'

        async with self.publish_lock:
            self.next_seq += 1
            seq = self.next_seq
            self.outstanding[seq] = (message, event_id)

            self.channel.basic_publish(exchange=self.exchange_name, 
                                    routing_key=routing_key, 
                                    body=message.model_dump_json(),
                                    mandatory=True)
        

    def on_delivery_confirmation(self, method_frame):
        method = method_frame.method
        delivery_tag = method.delivery_tag
        multiple = getattr(method, "multiple", False)
        kind = method.NAME.split('.')[-1]  # 'Ack' or 'Nack'

        seqs = [delivery_tag] if not multiple else [k for k in list(self.outstanding.keys()) if k <= delivery_tag]

        for seq in seqs:
            msg_data = self.outstanding.pop(seq, None)
            if msg_data:
                message, event_id = msg_data
                confirmation_type = 'ack' if kind == 'Ack' else 'nack'
                
                if event_id:
                    asyncio.run_coroutine_threadsafe(
                        self._notify_delivery_confirmation({
                            'type': confirmation_type, 
                            'event_id': event_id,
                            'message': message,
                            'seq': seq
                        }),
                        self.loop
                    )


    def on_returned_message(self, channel, method, properties, body):
        print("[RETURNED] unroutable message:", method, body)