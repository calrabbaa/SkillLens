from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api_schemas import MatchResult
from database import get_db
from services.match_service import calculate_match


router = APIRouter(
    prefix="/api/matches",
    tags=["matches"],
)


class MatchRequest(BaseModel):
    job_id: int
    resume_id: int


@router.post(
    "",
    response_model=MatchResult,
)
def create_match(
    request: MatchRequest,
    db: Session = Depends(get_db),
):
    try:
        return calculate_match(
            db=db,
            job_id=request.job_id,
            resume_id=request.resume_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
