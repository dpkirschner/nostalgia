import os
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient, ASGITransport

os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"
os.environ["CORS_ORIGINS"] = '["*"]'
os.environ["LOG_LEVEL"] = "INFO"

from app.models.location import Location
from app.models.tenancy import Tenancy
from app.models.memory_submission import MemorySubmission
from app.repositories.location_repository import ILocationRepository
from app.repositories.tenancy_repository import ITenancyRepository
from app.repositories.memory_repository import IMemoryRepository


@pytest.fixture
def mock_async_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def sample_location():
    return Location(
        id=1,
        lat=37.7749,
        lon=-122.4194,
        address="123 Market St, San Francisco, CA",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_tenancy():
    return Tenancy(
        id=1,
        location_id=1,
        business_name="Joe's Coffee",
        category="cafe",
        start_date=date(2020, 1, 1),
        end_date=None,
        is_current=True,
        sources={"google_maps": "https://example.com"},
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_memory():
    return MemorySubmission(
        id=1,
        location_id=1,
        business_name="Old Book Store",
        start_year=2010,
        end_year=2015,
        note="Great place for vintage books",
        proof_url="https://example.com/photo.jpg",
        source="anon",
        status="pending",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def mock_location_repository():
    mock_repo = AsyncMock(spec=ILocationRepository)
    mock_repo.get_by_id = AsyncMock()
    mock_repo.get_all = AsyncMock()
    mock_repo.create = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    mock_repo.exists = AsyncMock()
    mock_repo.count = AsyncMock()
    mock_repo.find_by_coordinates = AsyncMock()
    mock_repo.find_in_bounding_box = AsyncMock()
    mock_repo.find_with_current_tenancy = AsyncMock()
    return mock_repo


@pytest.fixture
def mock_tenancy_repository():
    mock_repo = AsyncMock(spec=ITenancyRepository)
    mock_repo.get_by_id = AsyncMock()
    mock_repo.get_all = AsyncMock()
    mock_repo.create = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    mock_repo.exists = AsyncMock()
    mock_repo.count = AsyncMock()
    mock_repo.find_by_location = AsyncMock()
    mock_repo.find_current_by_location = AsyncMock()
    mock_repo.find_by_business_name = AsyncMock()
    mock_repo.find_by_date_range = AsyncMock()
    return mock_repo


@pytest.fixture
def mock_memory_repository():
    mock_repo = AsyncMock(spec=IMemoryRepository)
    mock_repo.get_by_id = AsyncMock()
    mock_repo.get_all = AsyncMock()
    mock_repo.create = AsyncMock()
    mock_repo.update = AsyncMock()
    mock_repo.delete = AsyncMock()
    mock_repo.exists = AsyncMock()
    mock_repo.count = AsyncMock()
    mock_repo.find_by_location = AsyncMock()
    mock_repo.find_by_status = AsyncMock()
    mock_repo.find_pending = AsyncMock()
    return mock_repo


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from app.main import app

    for middleware in app.user_middleware:
        if hasattr(middleware, 'kwargs') and 'dispatch' in str(middleware.cls):
            continue

    yield

    for middleware_stack in [app.middleware_stack]:
        if middleware_stack and hasattr(middleware_stack, 'app'):
            current = middleware_stack
            while current:
                if hasattr(current, 'buckets'):
                    current.buckets.clear()
                    break
                current = getattr(current, 'app', None)


@pytest.fixture
async def async_client():
    from app.main import app

    app.dependency_overrides.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
        app.dependency_overrides.clear()
