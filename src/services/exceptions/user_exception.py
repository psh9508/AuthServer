class UserNotFoundError(Exception):
    # Raised when the user cannot be found
    pass

class EmailNotVerifiedError(Exception):
    # Raised when the email is not verified
    pass

class DuplicateEmailError(Exception):
    # Raised when the email already exists
    pass