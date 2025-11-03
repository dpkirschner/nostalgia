import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import set_correlation_id


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = str(uuid.uuid4())

        request.state.correlation_id = correlation_id

        set_correlation_id(correlation_id)

        response = await call_next(request)

        response.headers["X-Correlation-ID"] = correlation_id

        return response
