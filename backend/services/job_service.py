from sqlalchemy import select
from sqlalchemy.orm import Session

import models

from services.skill_extractor import extract_skills
from services.skill_normalizer import normalize_skill


def create_job(
    db: Session,
    description: str,
) -> int:
    """
    Analyze a job description and persist the job,
    skills, and job-skill relationships.

    Returns the newly created job ID.
    """

    try:
        # Ask the LLM to extract skills.
        result = extract_skills(description)

        # Create the job.
        job_record = models.Job(
            description=description,
        )

        db.add(job_record)
        db.flush()

        seen_skill_names: set[str] = set()

        for extracted_skill in result.skills:
            skill_name, skill_category = normalize_skill(
                extracted_skill.name,
                extracted_skill.category,
            )

            if not skill_name:
                continue

            normalized_lookup = skill_name.casefold()

            # Avoid duplicate skills in one LLM response.
            if normalized_lookup in seen_skill_names:
                continue

            seen_skill_names.add(normalized_lookup)

            # Check whether the canonical skill already exists.
            statement = select(models.Skill).where(
                models.Skill.name == skill_name
            )

            skill_record = db.scalar(statement)

            # Create it if necessary.
            if skill_record is None:
                skill_record = models.Skill(
                    name=skill_name,
                    category=skill_category,
                )

                db.add(skill_record)
                db.flush()

            # Create the relationship between the job and skill.
            job_skill = models.JobSkill(
                job_id=job_record.id,
                skill_id=skill_record.id,
                required=extracted_skill.required,
            )

            db.add(job_skill)

        db.commit()

        return job_record.id

    except Exception:
        db.rollback()
        raise
