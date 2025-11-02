from unittest.mock import patch
import pytest

from app.services.memory_service import MemoryService
from app.schemas.memory import MemorySubmissionCreate, MemorySubmissionResponse


class TestMemoryService:
    @pytest.fixture
    def service(self, mock_async_session, mock_memory_repository):
        with patch(
            "app.services.memory_service.SupabaseMemoryRepository",
            return_value=mock_memory_repository,
        ):
            return MemoryService(mock_async_session)

    async def test_submit_memory_creates_and_returns_response(
        self, service, mock_async_session, mock_memory_repository, sample_memory
    ):
        mock_memory_repository.create.return_value = sample_memory

        memory_data = MemorySubmissionCreate(
            location_id=1,
            business_name="Old Book Store",
            start_year=2010,
            end_year=2015,
            note="Great place for vintage books",
            proof_url="https://example.com/photo.jpg",
        )

        result = await service.submit_memory(memory_data)

        assert isinstance(result, MemorySubmissionResponse)
        assert result.id == 1
        assert result.business_name == "Old Book Store"
        assert result.status == "pending"
        mock_memory_repository.create.assert_called_once()
        mock_async_session.commit.assert_called_once()

    async def test_submit_memory_sets_defaults(
        self, service, mock_memory_repository, sample_memory
    ):
        mock_memory_repository.create.return_value = sample_memory

        memory_data = MemorySubmissionCreate(
            location_id=1,
            business_name="Old Book Store",
        )

        result = await service.submit_memory(memory_data)

        created_memory = mock_memory_repository.create.call_args[0][0]
        assert created_memory.source == "anon"
        assert created_memory.status == "pending"

    async def test_get_pending_reviews_returns_list(
        self, service, mock_memory_repository, sample_memory
    ):
        mock_memory_repository.find_pending.return_value = [sample_memory]

        result = await service.get_pending_reviews(limit=50)

        assert len(result) == 1
        assert result[0].status == "pending"
        mock_memory_repository.find_pending.assert_called_once_with(50)

    async def test_get_pending_reviews_empty_results(
        self, service, mock_memory_repository
    ):
        mock_memory_repository.find_pending.return_value = []

        result = await service.get_pending_reviews(limit=50)

        assert len(result) == 0

    async def test_get_by_location_returns_memories(
        self, service, mock_memory_repository, sample_memory
    ):
        mock_memory_repository.find_by_location.return_value = [sample_memory]

        result = await service.get_by_location(location_id=1)

        assert len(result) == 1
        assert result[0].location_id == 1
        mock_memory_repository.find_by_location.assert_called_once_with(1)

    async def test_get_by_location_empty_results(
        self, service, mock_memory_repository
    ):
        mock_memory_repository.find_by_location.return_value = []

        result = await service.get_by_location(location_id=999)

        assert len(result) == 0
