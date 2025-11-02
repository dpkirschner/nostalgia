from unittest.mock import MagicMock
import pytest

from app.db.supabase.supabase_memory_repository import SupabaseMemoryRepository


class TestSupabaseMemoryRepository:
    @pytest.fixture
    def repository(self, mock_async_session):
        return SupabaseMemoryRepository(mock_async_session)

    async def test_find_by_location_returns_memories(
        self, repository, mock_async_session, sample_memory
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_memory]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_location(location_id=1)

        assert len(result) == 1
        assert result[0] == sample_memory

    async def test_find_by_location_empty_results(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_location(location_id=999)

        assert len(result) == 0

    async def test_find_by_status_returns_filtered_memories(
        self, repository, mock_async_session, sample_memory
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_memory]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_status(status="pending")

        assert len(result) == 1
        assert result[0].status == "pending"

    async def test_find_by_status_approved(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_by_status(status="approved")

        assert len(result) == 0

    async def test_find_pending_returns_pending_memories(
        self, repository, mock_async_session, sample_memory
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_memory]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_pending(limit=50)

        assert len(result) == 1
        assert result[0].status == "pending"

    async def test_find_pending_respects_limit(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        await repository.find_pending(limit=10)

        mock_async_session.execute.assert_called_once()

    async def test_find_pending_empty_results(self, repository, mock_async_session):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await repository.find_pending(limit=50)

        assert len(result) == 0
