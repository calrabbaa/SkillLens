from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

import models

from api_schemas import ResumeDetail, ResumeSummary
from database import get_db
from services.resume_service import create_resume


router = APIRouter(
    prefix="/api/resumes",
    tags=["resumes"],
)


MAX_FILE_SIZE = 5 * 1024 * 1024


def get_resume_detail(
    db: Session,
    resume_id: int,
) -> ResumeDetail | None:

    statement = (
        select(models.Resume)
        .options(
            selectinload(models.Resume.skills)
            .selectinload(models.ResumeSkill.skill)
        )
        .where(models.Resume.id == resume_id)
    )

    resume = db.scalar(statement)

    if resume is None:
        return None

    return ResumeDetail(
        id=resume.id,
        filename=resume.filename,
        created_at=resume.created_at,
        skills=[
            {
                "name": resume_skill.skill.name,
                "category": resume_skill.skill.category,
            }
            for resume_skill in resume.skills
        ],
    )


@router.post(
    "",
    response_model=ResumeDetail,
    status_code=201,
)
async def upload_resume(
    file: Annotated[
        UploadFile,
        File(description="PDF CV"),
    ],
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The CV must be smaller than 5 MB.",
        )

    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file does not appear to be a valid PDF.",
        )

    try:
        resume_id = create_resume(
            db=db,
            filename=file.filename or "unknown.pdf",
            file_bytes=file_bytes,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(f"Resume processing failed: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Failed to process the CV.",
        ) from exc

    result = get_resume_detail(db, resume_id)

    if result is None:
        raise HTTPException(
            status_code=500,
            detail="CV was created but could not be retrieved.",
        )

    return result


@router.get(
    "",
    response_model=list[ResumeSummary],
)
def list_resumes(
    db: Session = Depends(get_db),
):
    statement = (
        select(models.Resume)
        .options(selectinload(models.Resume.skills))
        .order_by(models.Resume.created_at.desc())
    )

    resumes = db.scalars(statement).all()

    return [
        ResumeSummary(
            id=resume.id,
            filename=resume.filename,
            created_at=resume.created_at,
            skill_count=len(resume.skills),
        )
        for resume in resumes
    ]


@router.get(
    "/{resume_id}",
    response_model=ResumeDetail,
)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
):
    result = get_resume_detail(db, resume_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="CV not found.",
        )

    return result
