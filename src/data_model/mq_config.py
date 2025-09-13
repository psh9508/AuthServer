from typing import Union
from pydantic import BaseModel

class MQConfig(BaseModel):
    server_name: str
    exchange_name: str