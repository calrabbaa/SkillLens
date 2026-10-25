from io import BytesIO

from sqlalchemy import select
from sqlalchemy.orm import Session

import models

from services.pdf_extractor import extract_pdf_text
from services.skill_extractor import extract_skills
from services.skill_normalizer import normalize_skill


def create_resume(
    db: Session,
    filename: str,
    file_bytes: bytes,
    demo_session_id: str,
) -> int:
    """
    Extract text from a PDF CV, identify skills using the LLM,
    normalize them, and persist the result.
    """

    try:
        extracted_text = extract_pdf_text(file_bytes)

        result = extract_skills(extracted_text)

        resume = models.Resume(
            filename=filename,
            extracted_text=extracted_text,
            demo_session_id=demo_session_id,
        )

        db.add(resume)
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

            if normalized_lookup in seen_skill_names:
                continue

            seen_skill_names.add(normalized_lookup)

            statement = select(models.Skill).where(
                models.Skill.name == skill_name
            )

            skill = db.scalar(statement)

            if skill is None:
                skill = models.Skill(
                    name=skill_name,
                    category=skill_category,
                )

                db.add(skill)
                db.flush()

            resume_skill = models.ResumeSkill(
                resume_id=resume.id,
                skill_id=skill.id,
            )

            db.add(resume_skill)

        db.commit()

        return resume.id

    except Exception:
        db.rollback()
        raise
