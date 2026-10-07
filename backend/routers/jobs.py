from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

import models

from api_schemas import JobCreate, JobDetail, JobSummary
from database import get_db
from services.job_service import create_job


router = APIRouter(
    prefix="/api/jobs",
    tags=["jobs"],
)


def get_job_detail(
    db: Session,
    job_id: int,
) -> JobDetail | None:
    statement = (
        select(models.Job)
        .options(
            selectinload(models.Job.skills)
            .selectinload(models.JobSkill.skill)
        )
        .where(models.Job.id == job_id)
    )

    job = db.scalar(statement)

    if job is None:
        return None

    return JobDetail(
        id=job.id,
        description=job.description,
        created_at=job.created_at,
        skills=[
            {
                "name": job_skill.skill.name,
                "category": job_skill.skill.category,
                "required": job_skill.required,
            }
            for job_skill in job.skills
        ],
    )


@router.post(
    "",
    response_model=JobDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_job_endpoint(
    job: JobCreate,
    db: Session = Depends(get_db),
):
    job_id = create_job(
        db=db,
        description=job.description,
    )

    result = get_job_detail(db, job_id)

    if result is None:
        raise HTTPException(
            status_code=500,
            detail="Job was created but could not be retrieved.",
        )

    return result


@router.get(
    "",
    response_model=list[JobSummary],
)
def list_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    statement = (
        select(models.Job)
        .options(selectinload(models.Job.skills))
        .order_by(models.Job.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    jobs = db.scalars(statement).all()

    return [
        JobSummary(
            id=job.id,
            created_at=job.created_at,
            skill_count=len(job.skills),
        )
        for job in jobs
    ]


@router.get(
    "/{job_id}",
    response_model=JobDetail,
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    result = get_job_detail(db, job_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return result
