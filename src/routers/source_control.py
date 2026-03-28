from fastapi import APIRouter, Depends

from src.factories.source_control import get_source_control_service
from src.routers.models.base_response_model import BaseResponseModel
from src.routers.models.source_control import ProjectInfo
from src.services.source_control_service import SourceControlService

router = APIRouter(prefix="/source-control", tags=["source-control"])


@router.post("/access-token")
async def issue_access_token(
    request: ProjectInfo,
    source_control_service: SourceControlService = Depends(get_source_control_service),
) -> BaseResponseModel:
    result = source_control_service.issue_access_token(request)
    return BaseResponseModel(data=result)
