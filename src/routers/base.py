from fastapi import APIRouter
from src.routers.models.base import HealthCheckRes
from src.routers.models.base_response_model import BaseResponseModel

router = APIRouter()

@router.get('/healthcheck', tags=['health'])
async def healthcheck() -> BaseResponseModel:
    return BaseResponseModel(data=HealthCheckRes(message="Service is healthy"))