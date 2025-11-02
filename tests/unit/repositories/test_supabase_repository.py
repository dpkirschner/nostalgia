from unittest.mock import MagicMock
import pytest

from app.db.supabase.supabase_repository import SupabaseRepository
from app.models.location import Location


class TestSupabaseRepository:
    @pytest.fixture
    def repository(self, mock_async_session):
        return SupabaseRepository(mock_async_session, Location)

    async def test_get_by_id_returns_entity(
        self, repository, mock_async_session, sample_location
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_location
        mock_async_session.execute.return_value = mock_result

        result = await repository.get_by_id(1)

        assert result == sample_location
        mock_async_session.execute.assert_called_once()

    async def test_get_by_id_returns_none_when_not_found(
        self, repository, mock_async_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_async_session.execute.return_value = mock_result

        result = await repository.get_by_id(999)

        assert result is None

    async def test_get_all_returns_list(
        self, repository, mock_async_session, sample_location
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_location]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.get_all(skip=0, limit=10)

        assert len(result) == 1
        assert result[0] == sample_location

    async def test_create_adds_and_returns_entity(
        self, repository, mock_async_session, sample_location
    ):
        result = await repository.create(sample_location)

        mock_async_session.add.assert_called_once_with(sample_location)
        mock_async_session.flush.assert_called_once()
        mock_async_session.refresh.assert_called_once_with(sample_location)
        assert result == sample_location

    async def test_update_returns_updated_entity(
        self, repository, mock_async_session, sample_location
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_location
        mock_async_session.execute.return_value = mock_result

        updated_location = Location(
            id=1,
            lat=37.8,
            lon=-122.5,
            address="456 New St",
        )

        result = await repository.update(1, updated_location)

        assert result is not None
        assert result.lat == 37.8
        mock_async_session.flush.assert_called_once()

    async def test_update_returns_none_when_not_found(
        self, repository, mock_async_session
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_async_session.execute.return_value = mock_result

        updated_location = Location(id=999, lat=37.8, lon=-122.5, address="456 New St")

        result = await repository.update(999, updated_location)

        assert result is None

    async def test_delete_returns_true_when_deleted(
        self, repository, mock_async_session
    ):
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_async_session.execute.return_value = mock_result

        result = await repository.delete(1)

        assert result is True

    async def test_delete_returns_false_when_not_found(
        self, repository, mock_async_session
    ):
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_async_session.execute.return_value = mock_result

        result = await repository.delete(999)

        assert result is False

    async def test_exists_returns_true_when_found(
        self, repository, mock_async_session
    ):
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_async_session.execute.return_value = mock_result

        result = await repository.exists(1)

        assert result is True

    async def test_exists_returns_false_when_not_found(
        self, repository, mock_async_session
    ):
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_async_session.execute.return_value = mock_result

        result = await repository.exists(999)

        assert result is False

    async def test_count_returns_total(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        mock_async_session.execute.return_value = mock_result

        result = await repository.count()

        assert result == 42
