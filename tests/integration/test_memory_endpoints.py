from unittest.mock import AsyncMock
import pytest

from app.main import app
from app.api.memories import get_memory_service
from app.services.memory_service import MemoryService
from app.schemas.memory import MemorySubmissionResponse


class TestMemoryEndpoints:
    @pytest.fixture
    def mock_memory_service(self):
        return AsyncMock(spec=MemoryService)

    async def test_create_memory_submission_success(
        self, async_client, mock_memory_service
    ):
        mock_response = MemorySubmissionResponse(
            id=1,
            location_id=1,
            business_name="Old Book Store",
            status="pending",
        )
        mock_memory_service.submit_memory.return_value = mock_response

        app.dependency_overrides[get_memory_service] = lambda: mock_memory_service

        try:
            response = await async_client.post(
                "/v1/memories",
                json={
                    "location_id": 1,
                    "business_name": "Old Book Store",
                    "start_year": 2010,
                    "end_year": 2015,
                    "note": "Great place",
                    "proof_url": "https://example.com/photo.jpg",
                },
            )

            assert response.status_code == 202
            data = response.json()
            assert data["id"] == 1
            assert data["business_name"] == "Old Book Store"
            assert data["status"] == "pending"
        finally:
            app.dependency_overrides.clear()

    async def test_create_memory_submission_minimal_data(
        self, async_client, mock_memory_service
    ):
        mock_response = MemorySubmissionResponse(
            id=2,
            location_id=1,
            business_name="Test Business",
            status="pending",
        )
        mock_memory_service.submit_memory.return_value = mock_response

        app.dependency_overrides[get_memory_service] = lambda: mock_memory_service

        try:
            response = await async_client.post(
                "/v1/memories",
                json={
                    "location_id": 1,
                    "business_name": "Test Business",
                },
            )

            assert response.status_code == 202
            data = response.json()
            assert data["status"] == "pending"
        finally:
            app.dependency_overrides.clear()

    async def test_create_memory_submission_invalid_location_id(self, async_client):
        response = await async_client.post(
            "/v1/memories",
            json={
                "location_id": 0,
                "business_name": "Test",
            },
        )

        assert response.status_code == 422

    async def test_create_memory_submission_invalid_business_name(self, async_client):
        response = await async_client.post(
            "/v1/memories",
            json={
                "location_id": 1,
                "business_name": "",
            },
        )

        assert response.status_code == 422

    async def test_create_memory_submission_invalid_year_range(self, async_client):
        response = await async_client.post(
            "/v1/memories",
            json={
                "location_id": 1,
                "business_name": "Test",
                "start_year": 2020,
                "end_year": 2010,
            },
        )

        assert response.status_code == 422

    async def test_create_memory_submission_invalid_proof_url(self, async_client):
        response = await async_client.post(
            "/v1/memories",
            json={
                "location_id": 1,
                "business_name": "Test",
                "proof_url": "not-a-url",
            },
        )

        assert response.status_code == 422

    async def test_create_memory_submission_year_bounds(self, async_client):
        response = await async_client.post(
            "/v1/memories",
            json={
                "location_id": 1,
                "business_name": "Test",
                "start_year": 1700,
            },
        )

        assert response.status_code == 422

    async def test_create_memory_submission_note_too_long(self, async_client):
        response = await async_client.post(
            "/v1/memories",
            json={
                "location_id": 1,
                "business_name": "Test",
                "note": "x" * 2001,
            },
        )

        assert response.status_code == 422
