from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    name: str
    category: str


@dataclass(frozen=True)
class JobSkillRequirement:
    skill: Skill
    required: bool


def calculate_skill_match(
    job_skills: list[JobSkillRequirement],
    resume_skills: list[Skill],
) -> dict:
    """
    Compare job requirements against CV skills.

    This function is deliberately independent of:
    - FastAPI
    - SQLAlchemy
    - PostgreSQL
    - OpenAI

    That makes the core matching algorithm easy to test.
    """

    resume_skills_by_name = {
        skill.name.casefold(): skill
        for skill in resume_skills
    }

    required_matched: list[Skill] = []
    required_missing: list[Skill] = []

    preferred_matched: list[Skill] = []
    preferred_missing: list[Skill] = []

    job_skill_names: set[str] = set()

    for requirement in job_skills:
        skill = requirement.skill
        skill_key = skill.name.casefold()

        job_skill_names.add(skill_key)

        if skill_key in resume_skills_by_name:
            if requirement.required:
                required_matched.append(skill)
            else:
                preferred_matched.append(skill)
        else:
            if requirement.required:
                required_missing.append(skill)
            else:
                preferred_missing.append(skill)

    additional_resume_skills = [
        skill
        for skill_key, skill in resume_skills_by_name.items()
        if skill_key not in job_skill_names
    ]

    required_total = (
        len(required_matched)
        + len(required_missing)
    )

    preferred_total = (
        len(preferred_matched)
        + len(preferred_missing)
    )

    weighted_total = (
        (required_total * 2)
        + preferred_total
    )

    weighted_matched = (
        (len(required_matched) * 2)
        + len(preferred_matched)
    )

    if weighted_total == 0:
        overall_score = 0.0
    else:
        overall_score = (
            weighted_matched / weighted_total
        ) * 100

    return {
        "overall_score": round(overall_score, 1),
        "required_matched": [
            {
                "name": skill.name,
                "category": skill.category,
            }
            for skill in required_matched
        ],
        "required_missing": [
            {
                "name": skill.name,
                "category": skill.category,
            }
            for skill in required_missing
        ],
        "preferred_matched": [
            {
                "name": skill.name,
                "category": skill.category,
            }
            for skill in preferred_matched
        ],
        "preferred_missing": [
            {
                "name": skill.name,
                "category": skill.category,
            }
            for skill in preferred_missing
        ],
        "additional_resume_skills": [
            {
                "name": skill.name,
                "category": skill.category,
            }
            for skill in additional_resume_skills
        ],
    }
