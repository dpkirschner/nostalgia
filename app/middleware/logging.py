import json
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class JSONLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": round(process_time, 3),
            "client_ip": request.client.host if request.client else None,
        }

        print(json.dumps(log_data))

        return response
