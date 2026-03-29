import os

from src.services.source_control_models import IssuedAccessToken
from src.services.source_controlers.base import SourceControlClient


class GitLabSourceControl(SourceControlClient):
    def issue_access_token(self, repo_url: str) -> IssuedAccessToken:
        raise NotImplementedError("GitLab source control is not implemented yet.")
