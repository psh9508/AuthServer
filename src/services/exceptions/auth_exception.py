

from src.services.exceptions.app_base_error import AppBaseError


class EmailVerificationFailed(AppBaseError):
    status_code = 400
    code = "EmailVerificationFailed"
    message = "Email verification failed"