from typing import Generic, TypeVar

from pydantic import BaseModel, Field, model_validator

class BaseResponseData(BaseModel):
    message: str = Field(default="", exclude=True)

DataT = TypeVar('DataT', bound=BaseResponseData)

class BaseResponseModel(BaseModel, Generic[DataT]):
    code: str = "SUCCESS"
    message: str = ""
    data: DataT

    @model_validator(mode="after")
    def set_message(self):
        self.message = self.data.message
        return self