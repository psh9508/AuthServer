from pydantic import BaseModel

class LoggerConfig(BaseModel):
    level: str = "INFO"
