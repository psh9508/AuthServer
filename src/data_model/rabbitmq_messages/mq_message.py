from typing import Union
from pydantic import BaseModel

class MQMessage(BaseModel):
    take_id: Union[str, None] = None
    is_response_message: bool = False
    origin: str
    source: str
    target: str
    method: str