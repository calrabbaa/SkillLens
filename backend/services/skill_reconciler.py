from schemas import Skill, SkillExtractionResult
from services.skill_normalizer import normalize_skill


def reconcile_skills(
    description: str,
    result: SkillExtractionResult,
) -> SkillExtractionResult:
    """
    Normalize and deduplicate LLM-extracted skills.

    The LLM is responsible for identifying skills
    and determining whether they are required or optional.

    This function does not infer missing skills or
    override the LLM's requirement classifications.
    """

    merged: dict[str, Skill] = {}

    for skill in result.skills:
        name, category = normalize_skill(
            skill.name,
            skill.category,
        )

        if not name:
            continue

        key = name.casefold()

        if key not in merged:
            merged[key] = Skill(
                name=name,
                category=category,
                required=skill.required,
            )

    return SkillExtractionResult(
        skills=list(merged.values())
    )
