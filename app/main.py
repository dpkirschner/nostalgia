from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import locations, memories
from app.core.config import settings
from app.db.supabase import check_db_connection
from app.middleware.logging import JSONLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


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

app.add_middleware(JSONLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")

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
