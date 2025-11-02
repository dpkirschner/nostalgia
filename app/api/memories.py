from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter

from app.db.session import get_db
from app.models.memory_submission import MemorySubmission
from app.schemas.memory import MemorySubmissionCreate, MemorySubmissionResponse

router = APIRouter(prefix="/v1/memories", tags=["memories"])

memory_submission_counter = Counter(
    "wutbh_memory_submissions_total",
    "Total number of memory submissions",
    ["source"]
)


@router.post("", response_model=MemorySubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_memory_submission(
    memory: MemorySubmissionCreate,
    db: AsyncSession = Depends(get_db),
):
    submission = MemorySubmission(
        location_id=memory.location_id,
        business_name=memory.business_name,
        start_year=memory.start_year,
        end_year=memory.end_year,
        note=memory.note,
        proof_url=memory.proof_url,
        source="anon",
        status="pending",
    )

    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    memory_submission_counter.labels(source="anon").inc()

    return MemorySubmissionResponse(
        id=submission.id,
        location_id=submission.location_id,
        business_name=submission.business_name,
        status=submission.status,
    )
