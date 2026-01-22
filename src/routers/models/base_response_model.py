from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict

class BaseResponseData(BaseModel):
    message: str = Field(default="", exclude=True)

DataT = TypeVar('DataT', bound=BaseResponseData)

class BaseResponseModel(BaseModel, Generic[DataT]):
    code: str = "SUCCESS"
    message: str = ""
    data: DataT

    @model_validator(mode="after")
    def set_message(self):
        if self.data and hasattr(self.data, 'message'):
            self.message = self.data.message
        return self