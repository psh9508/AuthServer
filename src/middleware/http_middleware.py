from typing import Awaitable, Callable
from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.jwt_logic import JwtLogic

open_apis: list[str] = [
    '/docs',
    '/healthcheck', 
    '/user/login',
    '/user/signup',
]

class HttpMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            if request.method == 'OPTIONS' or request.url.path in open_apis:
                return await call_next(request)
            
            bearer_token = request.headers.get('Authorization')

            if not bearer_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header is missing"
                )

            access_token = bearer_token.replace('Bearer ', '', 1).replace('bearer ', '', 1)

            if await JwtLogic.adecode_access_token(access_token) is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired access token"
                )

            return await call_next(request)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
        