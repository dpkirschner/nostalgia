from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import locations, memories
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import http_exception_handler, unhandled_exception_handler
from app.db.postgres import check_db_connection
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.logging import JSONLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(log_level=settings.log_level, log_format=settings.log_format)
    logger.info(f"Starting {settings.app_name}")
    yield
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(JSONLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(locations.router)
app.include_router(memories.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    db_ok = await check_db_connection()
    status = "ok" if db_ok else "error"
    return {"status": status, "database": "connected" if db_ok else "disconnected"}
