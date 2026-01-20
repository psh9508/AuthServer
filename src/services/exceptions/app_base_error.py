from dataclasses import dataclass
from typing import ClassVar


@dataclass
class AppBaseError(Exception):
    message: ClassVar[str] 
    status_code: ClassVar[int]
    code: ClassVar[str]
    
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        required = {'status_code', 'code', 'message'}
        for field in required:
            if field not in cls.__dict__:
                 raise TypeError(f"Missing required field: {field}")
        
    def __post_init__(self):
        super().__init__(self.message)