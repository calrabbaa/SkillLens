import re

from schemas import Skill, SkillExtractionResult
from services.skill_detector import detect_explicit_skills
from services.skill_normalizer import (
    SKILL_CATEGORIES,
    normalize_skill,
)


SECTION_PATTERN = re.compile(
    r"\b("
    r"nice[\s-]+to[\s-]+have|"
    r"preferred(?:\s+qualifications)?|"
    r"bonus|optional|"
    r"requirements?|responsibilities|"
    r"must[\s-]+have|"
    r"required(?:\s+qualifications)?|"
    r"qualifications"
    r")\s*:",
    re.IGNORECASE,
)


def detect_skill_requirements(
    description: str,
) -> dict[str, bool]:
    """
    Return detected skills and their required status.

    True = required
    False = optional

    A required mention takes precedence over an optional one.
    """
    sections = []
    headings = list(SECTION_PATTERN.finditer(description))

    if headings:
        sections.append((description[:headings[0].start()], False))

    for index, heading in enumerate(headings):
        end = (
            headings[index + 1].start()
            if index + 1 < len(headings)
            else len(description)
        )

        section_text = description[heading.end():end]
        heading_name = heading.group(1).lower()

        optional = (
            heading_name.startswith("nice")
            or heading_name.startswith("preferred")
            or heading_name in {"bonus", "optional"}
        )

        sections.append((section_text, optional))

    if not headings:
        sections = [(description, False)]

    detected = {}

    for section_text, optional in sections:
        for name in detect_explicit_skills(section_text):
            required = not optional

            detected[name] = (
                detected.get(name, False) or required
            )

    return detected


def reconcile_skills(
    description: str,
    result: SkillExtractionResult,
) -> SkillExtractionResult:
    """
    Merge AI skills with deterministic detections,
    normalize aliases, and remove duplicates.
    """

    detected = detect_skill_requirements(description)
    merged: dict[str, Skill] = {}

    # Normalize and deduplicate AI-extracted skills.
    for skill in result.skills:
        name, category = normalize_skill(
            skill.name,
            skill.category,
        )

        key = name.casefold()

        required = detected.get(name, skill.required)

        if key in merged:
            merged[key].required = (
                merged[key].required or required
            )
        else:
            merged[key] = Skill(
                name=name,
                category=category,
                required=required,
            )

    # Add missing explicitly mentioned technologies.
    for name, required in sorted(detected.items()):
        canonical_name, category = normalize_skill(
            name,
            SKILL_CATEGORIES.get(name, "Other"),
        )

        key = canonical_name.casefold()

        if key in merged:
            # Explicit section classification takes precedence.
            merged[key].required = required
        else:
            merged[key] = Skill(
                name=canonical_name,
                category=category,
                required=required,
            )

    return SkillExtractionResult(
        skills=list(merged.values())
    )
