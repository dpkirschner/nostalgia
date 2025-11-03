import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class JSONLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        correlation_id = getattr(request.state, "correlation_id", "N/A")

        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": round(process_time, 3),
            "client_ip": request.client.host if request.client else None,
            "correlation_id": correlation_id,
        }

        if response.status_code >= 400:
            if response.status_code >= 500:
                logger.error("Server error", extra=log_data)
            else:
                logger.warning("Client error", extra=log_data)
        else:
            logger.info("Request completed", extra=log_data)

        return response
