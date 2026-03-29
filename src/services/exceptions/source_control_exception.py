from dataclasses import dataclass

from src.services.exceptions.app_base_error import AppBaseError


@dataclass
class UnsupportedSourceControlProviderError(AppBaseError):
    provider: str

    status_code = 400
    code = "UnsupportedSourceControlProviderError"
    message = "Unsupported source control provider"


@dataclass
class SourceControlProviderDisabledError(AppBaseError):
    provider: str

    status_code = 503
    code = "SourceControlProviderDisabledError"
    message = "Source control provider is disabled"


@dataclass
class InvalidSourceControlRepositoryUrlError(AppBaseError):
    repo_url: str

    status_code = 400
    code = "InvalidSourceControlRepositoryUrlError"
    message = "Invalid repository URL for source control provider"


@dataclass
class DuplicateScmConnectionError(AppBaseError):
    status_code = 409
    code = "DuplicateScmConnectionError"
    message = "SCM connection already exists"


@dataclass
class SourceControlEncryptionKeyNotConfiguredError(AppBaseError):
    status_code = 500
    code = "SourceControlEncryptionKeyNotConfiguredError"
    message = "SCM PEM encryption key is not configured"


@dataclass
class InvalidSourceControlEncryptionKeyError(AppBaseError):
    status_code = 500
    code = "InvalidSourceControlEncryptionKeyError"
    message = "SCM PEM encryption key is invalid"


@dataclass
class ScmConnectionNotFoundError(AppBaseError):
    project_id: int

    status_code = 404
    code = "ScmConnectionNotFoundError"
    message = "SCM connection not found"
