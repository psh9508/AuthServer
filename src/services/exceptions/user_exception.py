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

@dataclass
class UserNotFoundError(AppBaseError):
    # Raised when the user cannot be found
    status_code = 404
    code = "UserNotFoundError"
    message = "User not found"

@dataclass
class InvalidCredentialsError(AppBaseError):
    # Raised when the credentials are invalid
    login_attempts: int = 0

    status_code = 401
    code = "InvalidCredentialsError"
    message = "Invalid credentials"

@dataclass
class EmailNotVerifiedError(AppBaseError):
    # Raised when the email is not verified
    user_id: str

    status_code = 403
    code = "EmailNotVerifiedError"
    message = "AUTH_EMAIL_NOT_VERIFIED"

@dataclass
class DuplicateEmailError(AppBaseError):
    # Raised when the email already exists
    status_code = 409
    code = "DuplicateEmailError"
    message = "User with this email already exists"

@dataclass
class UserAlreadyVerifiedError(AppBaseError):
    # Raised when the user is already verified
    status_code = 409
    code = "UserAlreadyVerifiedError"
    message = "User is already verified"

@dataclass
class VerificationCodeExpiredError(AppBaseError):
    # Raised when the verification code has expired
    action: str = "request_new_code"

    status_code = 400
    code = "VerificationCodeExpiredError"
    message = "Verification code has expired"