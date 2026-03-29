from fastapi import APIRouter, Depends

from src.factories.source_control import get_source_control_service
from src.routers.models.base_response_model import BaseResponseModel
from src.routers.models.source_control import (
    ProjectInfo,
    ScmConnectionCreateReq,
    ScmConnectionRes,
    SourceControlAccessTokenRes,
)
from src.services.source_control_service import SourceControlService

router = APIRouter(prefix="/source_control", tags=["source_control"])


@router.post("/connections")
async def create_connection(
    request: ScmConnectionCreateReq,
    source_control_service: SourceControlService = Depends(get_source_control_service),
) -> BaseResponseModel:
    result = await source_control_service.acreate_connection(request)
    return BaseResponseModel[ScmConnectionRes](data=result)


@router.post("/access_token")
async def issue_access_token(
    request: ProjectInfo,
    source_control_service: SourceControlService = Depends(get_source_control_service),
) -> BaseResponseModel:
    result = await source_control_service.issue_access_token(request)
    return BaseResponseModel[SourceControlAccessTokenRes](data=result)
