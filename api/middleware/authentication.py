from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

API_KEY = "secure-api-key"


class AuthenticationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        if request.url.path in ["/", "/docs", "/openapi.json"]:
            return await call_next(request)

        api_key = request.headers.get("Authorization")

        if api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

        response = await call_next(request)

        return response