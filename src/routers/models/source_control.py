from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from src.routers.models.base_response_model import BaseResponseData


class ProjectInfo(BaseModel):
    project_id: int = Field(..., description="Project ID")


class ScmConnectionCreateReq(BaseModel):
    project_id: int = Field(..., description="Project ID")
    provider: Literal["github", "gitlab"] = Field(..., description="Source control provider")
    owner: str = Field(..., description="Repository owner")
    repo_name: str = Field(..., description="Repository name")
    app_id: str = Field(..., description="SCM app ID")
    installation_id: str = Field(..., description="SCM installation ID")
    pem: str = Field(..., description="SCM app private key PEM contents")


class ScmConnectionRes(BaseResponseData):
    model_config = ConfigDict(from_attributes=True)

    project_id: int = Field(..., description="Project ID")
    provider: Literal["github", "gitlab"] = Field(..., description="Source control provider")
    owner: str = Field(..., description="Repository owner")
    repo_name: str = Field(..., description="Repository name")
    app_id: str = Field(..., description="SCM app ID")
    installation_id: str = Field(..., description="SCM installation ID")
    is_active: bool = Field(..., description="Whether the connection is active")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Update time")


class SourceControlAccessTokenRes(BaseResponseData):
    provider: Literal["github", "gitlab"] = Field(..., description="Source control provider")
    access_token: str = Field(..., description="Access token for the source control provider")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_at: datetime | None = Field(default=None, description="Token expiration time")
    repo_url: AnyHttpUrl = Field(..., description="Repository URL of the project")
