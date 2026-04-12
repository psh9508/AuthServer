import traceback
import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])

SAURON_BASE_URL = "https://d20367he0nkpcu.cloudfront.net"


async def analyze_by_sauron(
    repository_id: int,
    error_message: str,
    stack_trace: str
) -> dict:
    request_body = {
        "repository_id": repository_id,
        "error_message": error_message,
        "stack_trace": stack_trace,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SAURON_BASE_URL}/analyze",
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
            repository_id=1,
            error_message=str(e),
            stack_trace=traceback.format_exc(),
        )
        return result
