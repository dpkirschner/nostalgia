from unittest.mock import AsyncMock
import pytest

from app.main import app
from app.api.locations import get_location_service
from app.services.location_service import LocationService
from app.schemas.location import LocationDetail, TimelineEntry


class TestLocationEndpoints:
    @pytest.fixture
    def mock_location_service(self):
        return AsyncMock(spec=LocationService)

    async def test_get_locations_success(self, async_client, mock_location_service):
        mock_data = [
            {
                "id": 1,
                "lat": 37.7749,
                "lon": -122.4194,
                "address": "123 Market St",
                "current_business": "Joe's Coffee",
                "current_category": "cafe",
            }
        ]
        mock_location_service.find_locations_in_area.return_value = mock_data

        app.dependency_overrides[get_location_service] = lambda: mock_location_service

        try:
            response = await async_client.get("/v1/locations?bbox=-122.5,37.7,-122.4,37.8")

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 1
            assert len(data["locations"]) == 1
            assert data["locations"][0]["id"] == 1
            assert data["locations"][0]["current_business"] == "Joe's Coffee"
        finally:
            app.dependency_overrides.clear()

    async def test_get_locations_invalid_bbox_format(self, async_client):
        response = await async_client.get("/v1/locations?bbox=invalid")

        assert response.status_code == 400
        assert "Invalid bbox format" in response.json()["detail"]

    async def test_get_locations_invalid_bbox_coordinates(self, async_client):
        response = await async_client.get("/v1/locations?bbox=-200,37.7,-122.4,37.8")

        assert response.status_code == 400
        assert "Longitude must be between" in response.json()["detail"]

    async def test_get_locations_empty_results(self, async_client, mock_location_service):
        mock_location_service.find_locations_in_area.return_value = []

        app.dependency_overrides[get_location_service] = lambda: mock_location_service

        try:
            response = await async_client.get("/v1/locations?bbox=-122.5,37.7,-122.4,37.8")

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 0
            assert len(data["locations"]) == 0
        finally:
            app.dependency_overrides.clear()

    async def test_get_locations_respects_limit(self, async_client, mock_location_service):
        mock_location_service.find_locations_in_area.return_value = []

        app.dependency_overrides[get_location_service] = lambda: mock_location_service

        try:
            response = await async_client.get(
                "/v1/locations?bbox=-122.5,37.7,-122.4,37.8&limit=100"
            )

            assert response.status_code == 200
            mock_location_service.find_locations_in_area.assert_called_once()
            call_args = mock_location_service.find_locations_in_area.call_args
            assert call_args[0][1] == 100
        finally:
            app.dependency_overrides.clear()

    async def test_get_location_detail_success(self, async_client, mock_location_service):
        mock_detail = LocationDetail(
            id=1,
            lat=37.7749,
            lon=-122.4194,
            address="123 Market St",
            timeline=[
                TimelineEntry(
                    business_name="Joe's Coffee",
                    category="cafe",
                    start_date=None,
                    end_date=None,
                    is_current=True,
                )
            ],
        )
        mock_location_service.get_location_by_id.return_value = mock_detail

        app.dependency_overrides[get_location_service] = lambda: mock_location_service

        try:
            response = await async_client.get("/v1/locations/1")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["address"] == "123 Market St"
            assert len(data["timeline"]) == 1
            assert data["timeline"][0]["business_name"] == "Joe's Coffee"
        finally:
            app.dependency_overrides.clear()

    async def test_get_location_detail_not_found(self, async_client, mock_location_service):
        mock_location_service.get_location_by_id.return_value = None

        app.dependency_overrides[get_location_service] = lambda: mock_location_service

        try:
            response = await async_client.get("/v1/locations/999")

            assert response.status_code == 404
            assert response.json()["detail"] == "Location not found"
        finally:
            app.dependency_overrides.clear()

    async def test_get_location_detail_with_empty_timeline(
        self, async_client, mock_location_service
    ):
        mock_detail = LocationDetail(
            id=1,
            lat=37.7749,
            lon=-122.4194,
            address="123 Market St",
            timeline=[],
        )
        mock_location_service.get_location_by_id.return_value = mock_detail

        app.dependency_overrides[get_location_service] = lambda: mock_location_service

        try:
            response = await async_client.get("/v1/locations/1")

            assert response.status_code == 200
            data = response.json()
            assert len(data["timeline"]) == 0
        finally:
            app.dependency_overrides.clear()
