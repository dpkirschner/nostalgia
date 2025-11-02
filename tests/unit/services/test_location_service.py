from unittest.mock import AsyncMock, patch
import pytest

from app.services.location_service import LocationService
from app.repositories.location_repository import BoundingBox
from app.schemas.location import LocationDetail, TimelineEntry


class TestLocationService:
    @pytest.fixture
    def service(self, mock_async_session, mock_location_repository, mock_tenancy_repository):
        with patch(
            "app.services.location_service.PostgresLocationRepository",
            return_value=mock_location_repository,
        ), patch(
            "app.services.location_service.PostgresTenancyRepository",
            return_value=mock_tenancy_repository,
        ):
            return LocationService(mock_async_session)

    async def test_get_location_by_id_returns_detail(
        self,
        service,
        mock_location_repository,
        mock_tenancy_repository,
        sample_location,
        sample_tenancy,
    ):
        mock_location_repository.get_by_id.return_value = sample_location
        mock_tenancy_repository.find_by_location.return_value = [sample_tenancy]

        result = await service.get_location_by_id(1)

        assert isinstance(result, LocationDetail)
        assert result.id == 1
        assert result.lat == 37.7749
        assert len(result.timeline) == 1
        assert result.timeline[0].business_name == "Joe's Coffee"

    async def test_get_location_by_id_returns_none_when_not_found(
        self, service, mock_location_repository
    ):
        mock_location_repository.get_by_id.return_value = None

        result = await service.get_location_by_id(999)

        assert result is None

    async def test_get_location_by_id_with_empty_timeline(
        self, service, mock_location_repository, mock_tenancy_repository, sample_location
    ):
        mock_location_repository.get_by_id.return_value = sample_location
        mock_tenancy_repository.find_by_location.return_value = []

        result = await service.get_location_by_id(1)

        assert isinstance(result, LocationDetail)
        assert len(result.timeline) == 0

    async def test_find_locations_in_area_returns_dict_list(
        self, service, mock_location_repository
    ):
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
        mock_location_repository.find_with_current_tenancy.return_value = mock_data

        bbox = BoundingBox(west=-122.5, south=37.7, east=-122.4, north=37.8)
        result = await service.find_locations_in_area(bbox, limit=300)

        assert len(result) == 1
        assert result[0]["id"] == 1
        mock_location_repository.find_with_current_tenancy.assert_called_once_with(
            bbox, 300
        )

    async def test_find_locations_in_area_empty_results(
        self, service, mock_location_repository
    ):
        mock_location_repository.find_with_current_tenancy.return_value = []

        bbox = BoundingBox(west=0.0, south=0.0, east=1.0, north=1.0)
        result = await service.find_locations_in_area(bbox, limit=300)

        assert len(result) == 0

    async def test_create_location_returns_existing_when_duplicate(
        self,
        service,
        mock_location_repository,
        mock_tenancy_repository,
        sample_location,
    ):
        mock_location_repository.find_by_coordinates.return_value = sample_location
        mock_location_repository.get_by_id.return_value = sample_location
        mock_tenancy_repository.find_by_location.return_value = []

        result = await service.create_location(37.7749, -122.4194, "123 Market St")

        assert isinstance(result, LocationDetail)
        assert result.id == 1
        mock_location_repository.create.assert_not_called()

    async def test_create_location_creates_new_when_not_exists(
        self,
        service,
        mock_async_session,
        mock_location_repository,
        mock_tenancy_repository,
        sample_location,
    ):
        mock_location_repository.find_by_coordinates.return_value = None
        mock_location_repository.create.return_value = sample_location
        mock_location_repository.get_by_id.return_value = sample_location
        mock_tenancy_repository.find_by_location.return_value = []

        result = await service.create_location(37.7749, -122.4194, "123 Market St")

        assert isinstance(result, LocationDetail)
        mock_location_repository.create.assert_called_once()
        mock_async_session.commit.assert_called_once()
