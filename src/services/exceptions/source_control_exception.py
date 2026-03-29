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
