import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter


rate_limited_counter = Counter(
    "wutbh_rate_limited_total",
    "Total number of rate limited requests",
    ["endpoint"]
)


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_refill

        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.buckets: dict[tuple[str, str], TokenBucket] = defaultdict(
            lambda: TokenBucket(0, 0)
        )

        self.limits = {
            "GET": (100, 300),
            "POST:/v1/memories": (5, 600),
        }

    def get_bucket(self, ip: str, endpoint_key: str) -> TokenBucket:
        key = (ip, endpoint_key)
        if key not in self.buckets:
            capacity, window = self.limits.get(endpoint_key, self.limits["GET"])
            refill_rate = capacity / window
            self.buckets[key] = TokenBucket(capacity, refill_rate)
        return self.buckets[key]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in ["/healthz", "/readyz", "/metrics"]:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"

        if request.method == "POST" and request.url.path == "/v1/memories":
            endpoint_key = "POST:/v1/memories"
        else:
            endpoint_key = request.method

        bucket = self.get_bucket(ip, endpoint_key)

        if not bucket.consume():
            rate_limited_counter.labels(endpoint=endpoint_key).inc()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "endpoint": endpoint_key,
                    "retry_after": 60
                }
            )

        return await call_next(request)
