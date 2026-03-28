from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, Field

from src.routers.models.base_response_model import BaseResponseData


class ProjectInfo(BaseResponseData):
    project_id: int = Field(..., description="Project ID")
    source_code_type: Literal["github", "gitlab"] = Field(
        ...,
        description="Source code type",
    )
    repo_url: AnyHttpUrl = Field(..., description="Repository URL of the project")


class SourceControlAccessTokenRes(BaseResponseData):
    provider: Literal["github", "gitlab"] = Field(..., description="Source control provider")
    access_token: str = Field(..., description="Access token for the source control provider")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_at: datetime | None = Field(default=None, description="Token expiration time")
    repo_url: AnyHttpUrl = Field(..., description="Repository URL of the project")
