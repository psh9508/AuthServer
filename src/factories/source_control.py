from src.services.source_control_service import SourceControlService
from src.services.source_controlers.base import SourceControlClient


def get_source_control_client(provider: str) -> SourceControlClient:
    selected_provider = provider.strip().lower()

    if selected_provider == "github":
        from src.services.source_controlers.github_source_control import GitHubSourceControl
        return GitHubSourceControl()

    if selected_provider == "gitlab":
        from src.services.source_controlers.gitlab_source_control import GitLabSourceControl
        return GitLabSourceControl()

    raise ValueError(
        f"Unsupported source control provider: {selected_provider}"
    )


def get_source_control_service() -> SourceControlService:
    return SourceControlService(get_source_control_client)
