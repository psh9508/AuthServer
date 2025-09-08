from fastapi import APIRouter

router = APIRouter()

@router.get('/healthcheck', tags=['health'])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}