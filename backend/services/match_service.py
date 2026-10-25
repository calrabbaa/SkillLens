from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

import models

from services.match_engine import (
    JobSkillRequirement,
    Skill,
    calculate_skill_match,
)


def get_job_for_matching(
    db: Session,
    job_id: int,
) -> models.Job | None:
    statement = (
        select(models.Job)
        .options(
            selectinload(models.Job.skills)
            .selectinload(models.JobSkill.skill)
        )
        .where(models.Job.id == job_id)
    )

    return db.scalar(statement)


def get_resume_for_matching(
    db: Session,
    resume_id: int,
) -> models.Resume | None:
    statement = (
        select(models.Resume)
        .options(
            selectinload(models.Resume.skills)
            .selectinload(models.ResumeSkill.skill)
        )
        .where(models.Resume.id == resume_id)
    )

    return db.scalar(statement)


def calculate_match(
    db: Session,
    job_id: int,
    resume_id: int,
) -> dict:
    job = get_job_for_matching(db, job_id)

    if job is None:
        raise ValueError("Job not found.")

    resume = get_resume_for_matching(db, resume_id)

    if resume is None:
        raise ValueError("CV not found.")

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

    result = calculate_skill_match(
        job_skills=job_skills,
        resume_skills=resume_skills,
    )

    return {
        "job_id": job.id,
        "resume_id": resume.id,
        **result,
    }
