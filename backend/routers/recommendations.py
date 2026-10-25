from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api_schemas import RecommendationResponse
from database import get_db
from services.match_service import (
    get_job_for_matching,
    get_resume_for_matching,
)
from services.match_engine import (
    JobSkillRequirement,
    Skill,
    calculate_skill_match,
)
from services.recommendation_service import (
    generate_recommendations,
)


router = APIRouter(
    prefix="/api/recommendations",
    tags=["recommendations"],
)


class RecommendationRequest(BaseModel):
    job_id: int
    resume_id: int


@router.post(
    "",
    response_model=RecommendationResponse,
)
def create_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):
    job = get_job_for_matching(
        db,
        request.job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    resume = get_resume_for_matching(
        db,
        request.resume_id,
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="CV not found.",
        )

    job_skills = [
        JobSkillRequirement(
            skill=Skill(
                name=job_skill.skill.name,
                category=job_skill.skill.category,
            ),
            required=job_skill.required,
        )
        for job_skill in job.skills
    ]

    resume_skills = [
        Skill(
            name=resume_skill.skill.name,
            category=resume_skill.skill.category,
        )
        for resume_skill in resume.skills
    ]

    match_result = calculate_skill_match(
        job_skills=job_skills,
        resume_skills=resume_skills,
    )

    missing_skills = (
        match_result["required_missing"]
        + match_result["preferred_missing"]
    )

    result = generate_recommendations(
        job_description=job.description,
        missing_skills=missing_skills,
    )

    return {
        "recommendations": [
            recommendation.model_dump()
            for recommendation in result.recommendations
        ]
    }
