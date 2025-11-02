from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter

from app.db.postgres import get_db
from app.services.memory_service import MemoryService
from app.schemas.memory import MemorySubmissionCreate, MemorySubmissionResponse

router = APIRouter(prefix="/v1/memories", tags=["memories"])

memory_submission_counter = Counter(
    "wutbh_memory_submissions_total",
    "Total number of memory submissions",
    ["source"]
)


def get_memory_service(session: AsyncSession = Depends(get_db)) -> MemoryService:
    return MemoryService(session)


@router.post("", response_model=MemorySubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_memory_submission(
    memory: MemorySubmissionCreate,
    service: MemoryService = Depends(get_memory_service),
):
    response = await service.submit_memory(memory)

    memory_submission_counter.labels(source="anon").inc()

    return response
