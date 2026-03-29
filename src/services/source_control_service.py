from sqlalchemy.ext.asyncio import AsyncSession

from src.core.scm_pem_cipher import ScmPemCipher
from src.repositories.scm_connection_repository import ScmConnectionRepository
from config.config import is_source_control_provider_enabled
from src.routers.models.source_control import (
    ProjectInfo,
    ScmConnectionCreateReq,
    ScmConnectionRes,
    SourceControlAccessTokenRes,
)
from src.services.exceptions.source_control_exception import (
    SourceControlProviderDisabledError,
    UnsupportedSourceControlProviderError,
)
from src.services.source_controlers.base import SourceControlClient


class SourceControlService:
    def __init__(self, session: AsyncSession | None = None):
        self.scm_connection_repo = ScmConnectionRepository(session) if session is not None else None

    async def issue_access_token(self, project_info: ProjectInfo) -> SourceControlAccessTokenRes:
        if self.scm_connection_repo is None:
            raise RuntimeError("SCM connection repository is not initialized.")

        scm_connection = await self.scm_connection_repo.aget_active_by_project_id(project_info.project_id)
        repo_url = self._build_repo_url(
            provider=scm_connection.provider,
            owner=scm_connection.owner,
            repo_name=scm_connection.repo_name,
        )
        source_control_client = self._get_source_control_client(
            provider=scm_connection.provider,
            app_id=scm_connection.app_id,
            installation_id=scm_connection.installation_id,
            pem_contents=ScmPemCipher.decrypt(scm_connection.encrypted_pem),
        )
        issued_token = source_control_client.issue_access_token(repo_url)

        return SourceControlAccessTokenRes(
            provider=scm_connection.provider,
            access_token=issued_token.access_token,
            expires_at=issued_token.expires_at,
            repo_url=repo_url,
        )

    def _get_source_control_client(
        self,
        provider: str,
        app_id: str | None = None,
        installation_id: str | None = None,
        pem_contents: str | None = None,
    ) -> SourceControlClient:
        selected_provider = provider.strip().lower()

        if selected_provider == "github":
            self._validate_provider_enabled(selected_provider)
            from src.services.source_controlers.github_source_control import GitHubSourceControl
            return GitHubSourceControl(
                app_id=app_id,
                installation_id=installation_id,
                pem_contents=pem_contents,
            )

        # if selected_provider == "gitlab":
        #     self._validate_provider_enabled(selected_provider)
        #     from src.services.source_controlers.gitlab_source_control import GitLabSourceControl
        #     return GitLabSourceControl()

        raise UnsupportedSourceControlProviderError(provider=selected_provider)

    def _validate_provider_enabled(self, provider: str) -> None:
        if not is_source_control_provider_enabled(provider):
            raise SourceControlProviderDisabledError(provider=provider)

    def _build_repo_url(self, provider: str, owner: str, repo_name: str) -> str:
        selected_provider = provider.strip().lower()

        if selected_provider == "github":
            return f"https://github.com/{owner}/{repo_name}"

        # if selected_provider == "gitlab":
        #     return f"https://gitlab.com/{owner}/{repo_name}"

        raise UnsupportedSourceControlProviderError(provider=selected_provider)

    async def acreate_connection(self, request: ScmConnectionCreateReq) -> ScmConnectionRes:
        if self.scm_connection_repo is None:
            raise RuntimeError("SCM connection repository is not initialized.")

        encrypted_pem = ScmPemCipher.encrypt(request.pem)
        created_connection = await self.scm_connection_repo.acreate(
            project_id=request.project_id,
            provider=request.provider,
            owner=request.owner,
            repo_name=request.repo_name,
            app_id=request.app_id,
            installation_id=request.installation_id,
            encrypted_pem=encrypted_pem,
        )

        return ScmConnectionRes.model_validate(created_connection)
