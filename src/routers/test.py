from fastapi import APIRouter

from src.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/")
async def test_error():
    logger.error("test_error endpoint called - triggering error")
    raise ValueError("intentional test error")
