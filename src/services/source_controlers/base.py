from abc import ABC, abstractmethod

from src.services.source_control_models import IssuedAccessToken


class SourceControlClient(ABC):
    @abstractmethod
    def issue_access_token(self, repo_url: str) -> IssuedAccessToken:
        raise NotImplementedError
