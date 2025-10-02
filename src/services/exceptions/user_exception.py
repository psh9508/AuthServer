from dataclasses import dataclass


class UserNotFoundError(Exception):
    # Raised when the user cannot be found
    pass

@dataclass
class EmailNotVerifiedError(Exception):
    # Raised when the email is not verified
    user_id: str
    pass

class DuplicateEmailError(Exception):
    # Raised when the email already exists
    pass

class UserAlreadyVerifiedError(Exception):
    # Raised when the user is already verified
    pass

class VerificationCodeExpiredError(Exception):
    # Raised when the verification code has expired
    pass