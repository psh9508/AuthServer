import json
import os
from datetime import datetime
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.core.jwt_logic import JwtLogic
from src.services.exceptions.source_control_exception import InvalidSourceControlRepositoryUrlError
from src.services.source_control_models import IssuedAccessToken
from src.services.source_controlers.base import SourceControlClient


class GitHubSourceControl(SourceControlClient):
    def __init__(
        self,
        app_id: str | None = None,
        installation_id: str | None = None,
        pem_contents: str | None = None,
    ) -> None:
        self.app_id = app_id or os.getenv("GITHUB_APP_ID")
        self.installation_id = installation_id or os.getenv("GITHUB_INSTALLATION_ID")
        self.pem_contents = self._load_pem_contents(pem_contents or os.getenv("GITHUB_PEM"))

    def issue_access_token(self, repo_url: str) -> IssuedAccessToken:
        github_app_jwt = JwtLogic.create_github_app_jwt(
            app_id=self._get_app_id(),
            private_key=self.pem_contents,
        )
        request_body = json.dumps({
            "repositories": [self._extract_repository_name(repo_url)],
        }).encode("utf-8")

        request = Request(
            url=self._get_installation_access_token_url(),
            data=request_body,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {github_app_jwt}",
                "Content-Type": "application/json",
                "User-Agent": "AuthServer",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Failed to issue GitHub installation access token: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Failed to reach GitHub for installation access token: {exc}") from exc

        access_token = payload.get("token")
        if not access_token:
            raise RuntimeError("GitHub response did not include an installation access token.")

        expires_at = payload.get("expires_at")
        return IssuedAccessToken(
            access_token=access_token,
            expires_at=self._parse_expires_at(expires_at),
        )

    def _get_app_id(self) -> str:
        if not self.app_id or self.app_id == "NONE":
            raise ValueError("GITHUB_APP_ID must be set.")

        return self.app_id

    def _get_installation_id(self) -> str:
        if not self.installation_id or self.installation_id == "NONE":
            raise ValueError("GITHUB_INSTALLATION_ID must be set.")

        return self.installation_id

    def _get_installation_access_token_url(self) -> str:
        installation_id = self._get_installation_id()
        return f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    def _load_pem_contents(self, pem_contents: str | None) -> str:
        if not pem_contents or pem_contents == "NONE":
            raise ValueError("GITHUB_PEM must be set to PEM contents.")

        normalized_pem = pem_contents.replace("\\n", "\n").strip()
        if "BEGIN" not in normalized_pem or "PRIVATE KEY" not in normalized_pem:
            raise ValueError("GITHUB_PEM must contain a valid PEM private key.")

        return normalized_pem

    def _parse_expires_at(self, expires_at: str | None) -> datetime | None:
        if not expires_at:
            return None

        return datetime.fromisoformat(expires_at.replace("Z", "+00:00"))

    def _extract_repository_name(self, repo_url: str) -> str:
        parsed_url = urlparse(repo_url)
        path_parts = [part for part in parsed_url.path.split("/") if part]

        if len(path_parts) < 2:
            raise InvalidSourceControlRepositoryUrlError(repo_url=repo_url)

        repository_name = path_parts[1]
        if repository_name.endswith(".git"):
            repository_name = repository_name[:-4]

        if not repository_name:
            raise InvalidSourceControlRepositoryUrlError(repo_url=repo_url)

        return repository_name
