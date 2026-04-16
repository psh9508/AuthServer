import traceback
import httpx
from fastapi import APIRouter

from src.config.settings import get_settings

router = APIRouter(prefix="/test", tags=["test"])


async def analyze_by_sauron(
    error_message: str,
    stack_trace: str
) -> dict:
    settings = get_settings()
    request_body = {
        "repository_id": settings.sauron.repository_id,
        "error_message": error_message,
        "stack_trace": stack_trace,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.sauron.endpoint}/analyze",
            json=request_body,
            headers={"Content-Type": "application/json"},
        )
        return response.json()


@router.get("/")
async def test_error():
    try:
        return 1 / 0
    except Exception as e:
        result = await analyze_by_sauron(
            error_message=str(e),
            stack_trace=traceback.format_exc(),
        )
        return result
