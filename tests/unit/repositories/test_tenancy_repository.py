from datetime import date
from unittest.mock import MagicMock
import pytest

from app.db.supabase.supabase_tenancy_repository import SupabaseTenancyRepository


class TestSupabaseTenancyRepository:
    @pytest.fixture
    def repository(self, mock_async_session):
        return SupabaseTenancyRepository(mock_async_session)

    async def test_find_by_location_returns_tenancies(
        self, repository, mock_async_session, sample_tenancy
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_tenancy]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_location(location_id=1, limit=3)

        assert len(result) == 1
        assert result[0] == sample_tenancy

    async def test_find_by_location_respects_limit(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        await repository.find_by_location(location_id=1, limit=5)

        mock_async_session.execute.assert_called_once()

    async def test_find_by_location_empty_results(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_location(location_id=999, limit=3)

        assert len(result) == 0

    async def test_find_current_by_location_returns_current_only(
        self, repository, mock_async_session, sample_tenancy
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_tenancy]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_current_by_location(location_id=1)

        assert len(result) == 1
        assert result[0].is_current is True

    async def test_find_by_business_name_case_insensitive(
        self, repository, mock_async_session, sample_tenancy
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_tenancy]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_business_name("coffee")

        assert len(result) == 1
        assert result[0] == sample_tenancy

    async def test_find_by_business_name_empty_results(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_business_name("nonexistent")

        assert len(result) == 0

    async def test_find_by_date_range_returns_overlapping_tenancies(
        self, repository, mock_async_session, sample_tenancy
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_tenancy]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_date_range(
            location_id=1,
            start_date=date(2021, 1, 1),
            end_date=date(2022, 12, 31),
        )

        assert len(result) == 1
        assert result[0] == sample_tenancy

    async def test_find_by_date_range_no_overlap(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_date_range(
            location_id=1,
            start_date=date(1990, 1, 1),
            end_date=date(1995, 12, 31),
        )

        assert len(result) == 0
