from dataclasses import asdict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from prometheus_client import make_asgi_app
import uvicorn
import main_app
from src.services.exceptions.user_exception import AppBaseError
from src.routers.user import router as user_router
from src.routers.base import router as base_router
from src.routers.auth import router as auth_router

app = main_app.get_main_app()
app.mount("/metrics", make_asgi_app())

app.include_router(user_router)
app.include_router(base_router)
app.include_router(auth_router)

@app.exception_handler(AppBaseError)
async def global_exception_handler(_: Request, exc: AppBaseError):
    error_data = asdict(exc)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": error_data
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": "HTTP_ERROR",
            "message": "",
            "data": exc.detail,
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "data": None
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)