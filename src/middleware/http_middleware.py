from typing import Awaitable, Callable
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from src.core.jwt_logic import JwtLogic

open_apis: list[str] = [
    '/',
    '/docs',
    '/docs/',
    '/health',
    '/health/',
    '/docs/oauth2-redirect',
    '/healthcheck',
    '/metrics',
    '/metrics/',
    '/openapi.json',
    '/redoc',
    '/user/login',
    '/user/signup',
    '/auth/user_verification',
    '/auth/regenerate_verification_code',
    '/test',
    '/test/',
]

class HttpMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            if (
                request.method == 'OPTIONS'
                or request.url.path in open_apis
            ):
                return await call_next(request)
            
            bearer_token = request.headers.get('Authorization')

            if not bearer_token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authorization header is missing"}
                )

            access_token = bearer_token.replace('Bearer ', '', 1).replace('bearer ', '', 1)

            if await JwtLogic.adecode_access_token(access_token) is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired access token"}
                )

            return await call_next(request)
        except Exception:
            # raise it as itself not in production mode.
            raise
        
