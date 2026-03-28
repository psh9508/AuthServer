from typing import Callable

from src.routers.models.source_control import ProjectInfo, SourceControlAccessTokenRes
from src.services.source_controlers.base import SourceControlClient


class SourceControlService:
    def __init__(
        self,
        source_control_client_factory: Callable[[str], SourceControlClient],
    ) -> None:
        self.source_control_client_factory = source_control_client_factory

    def issue_access_token(self, project_info: ProjectInfo) -> SourceControlAccessTokenRes:
        source_control_client = self.source_control_client_factory(project_info.source_code_type)
        issued_token = source_control_client.issue_access_token()

        return SourceControlAccessTokenRes(
            provider=project_info.source_code_type,
            access_token=issued_token.access_token,
            expires_at=issued_token.expires_at,
            repo_url=project_info.repo_url,
        )
