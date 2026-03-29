from config.config import is_source_control_provider_enabled
from src.routers.models.source_control import ProjectInfo, SourceControlAccessTokenRes
from src.services.exceptions.source_control_exception import (
    SourceControlProviderDisabledError,
    UnsupportedSourceControlProviderError,
)
from src.services.source_controlers.base import SourceControlClient


class SourceControlService:
    def issue_access_token(self, project_info: ProjectInfo) -> SourceControlAccessTokenRes:
        source_control_client = self._get_source_control_client(project_info.source_code_type)
        issued_token = source_control_client.issue_access_token(str(project_info.repo_url))

        return SourceControlAccessTokenRes(
            provider=project_info.source_code_type,
            access_token=issued_token.access_token,
            expires_at=issued_token.expires_at,
            repo_url=project_info.repo_url,
        )

    def _get_source_control_client(self, provider: str) -> SourceControlClient:
        selected_provider = provider.strip().lower()

        if selected_provider == "github":
            self._validate_provider_enabled(selected_provider)
            from src.services.source_controlers.github_source_control import GitHubSourceControl
            return GitHubSourceControl()

        if selected_provider == "gitlab":
            self._validate_provider_enabled(selected_provider)
            from src.services.source_controlers.gitlab_source_control import GitLabSourceControl
            return GitLabSourceControl()

        raise UnsupportedSourceControlProviderError(provider=selected_provider)

    def _validate_provider_enabled(self, provider: str) -> None:
        if not is_source_control_provider_enabled(provider):
            raise SourceControlProviderDisabledError(provider=provider)
