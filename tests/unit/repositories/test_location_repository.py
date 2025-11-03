from unittest.mock import MagicMock
import pytest

from app.db.supabase.supabase_location_repository import SupabaseLocationRepository
from app.repositories.location_repository import BoundingBox


class TestSupabaseLocationRepository:
    @pytest.fixture
    def repository(self, mock_async_session):
        return SupabaseLocationRepository(mock_async_session)

    async def test_find_by_coordinates_exact_match(
        self, repository, mock_async_session, sample_location
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_location
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_coordinates(37.7749, -122.4194)

        assert result == sample_location
        mock_async_session.execute.assert_called_once()

    async def test_find_by_coordinates_with_tolerance(
        self, repository, mock_async_session, sample_location
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_location
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_coordinates(37.7750, -122.4195, tolerance=0.001)

        assert result == sample_location

    async def test_find_by_coordinates_returns_none_when_not_found(
        self, repository, mock_async_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_coordinates(40.0, -120.0)

        assert result is None

    async def test_find_in_bounding_box_returns_locations(
        self, repository, mock_async_session, sample_location
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_location]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        bbox = BoundingBox(west=-122.5, south=37.7, east=-122.4, north=37.8)
        result = await repository.find_in_bounding_box(bbox, limit=300)

        assert len(result) == 1
        assert result[0] == sample_location

    async def test_find_in_bounding_box_empty_results(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        bbox = BoundingBox(west=0.0, south=0.0, east=1.0, north=1.0)
        result = await repository.find_in_bounding_box(bbox, limit=300)

        assert len(result) == 0

    async def test_find_with_current_tenancy_returns_dict_results(
        self, repository, mock_async_session
    ):
        mock_row = MagicMock()
        mock_row._mapping = {
            "id": 1,
            "lat": 37.7749,
            "lon": -122.4194,
            "address": "123 Market St",
            "current_business": "Joe's Coffee",
            "current_category": "cafe",
        }
        mock_result = MagicMock()
        mock_result.__iter__.return_value = [mock_row]
        mock_async_session.execute.return_value = mock_result

        bbox = BoundingBox(west=-122.5, south=37.7, east=-122.4, north=37.8)
        result = await repository.find_with_current_tenancy(bbox, limit=300)

        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["current_business"] == "Joe's Coffee"

    async def test_find_with_current_tenancy_respects_limit(self, repository, mock_async_session):
        mock_async_session.execute.return_value = MagicMock()

        bbox = BoundingBox(west=-122.5, south=37.7, east=-122.4, north=37.8)
        await repository.find_with_current_tenancy(bbox, limit=100)

        call_args = mock_async_session.execute.call_args
        assert call_args[0][1]["limit"] == 100
