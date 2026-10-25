from schemas import Skill, SkillExtractionResult
from services.skill_reconciler import reconcile_skills


def test_adds_skills_missing_from_ai():
    description = (
        "Requirements: Python, FastAPI, Docker."
    )

    ai_result = SkillExtractionResult(
        skills=[
            Skill(
                name="Python",
                category="Programming",
                required=True,
            )
        ]
    )

    result = reconcile_skills(description, ai_result)

    names = {skill.name for skill in result.skills}

    assert {"Python", "FastAPI", "Docker"} <= names

def test_preserves_optional_skills():
    description = (
        "Requirements: Python.\n"
        "Nice to have: GitHub Actions."
    )

    result = reconcile_skills(
        description,
        SkillExtractionResult(skills=[]),
    )

    skills = {skill.name: skill for skill in result.skills}

    assert skills["Python"].required is True
    assert skills["GitHub Actions"].required is False

def test_avoids_duplicate_canonical_skills():
    description = "Requirements: PostgreSQL."

    ai_result = SkillExtractionResult(
        skills=[
            Skill(
                name="Postgres",
                category="Databases",
                required=True,
            )
        ]
    )

    result = reconcile_skills(description, ai_result)

    assert len(result.skills) == 1

def test_merges_ai_alias_duplicates():
    description = "Requirements: PostgreSQL."

    ai_result = SkillExtractionResult(
        skills=[
            Skill(
                name="Postgres",
                category="Databases",
                required=True,
            ),
            Skill(
                name="PostgreSQL",
                category="Databases",
                required=True,
            ),
        ]
    )

    result = reconcile_skills(description, ai_result)

    assert len(result.skills) == 1
    assert result.skills[0].name == "PostgreSQL"

def test_corrects_optional_skill_classification():
    description = (
        "Requirements: Python.\n"
        "Nice to have: GitHub Actions."
    )

    ai_result = SkillExtractionResult(
        skills=[
            Skill(
                name="GitHub Actions",
                category="DevOps",
                required=True,
            ),
        ]
    )

    result = reconcile_skills(description, ai_result)

    skills = {skill.name: skill for skill in result.skills}

    assert skills["GitHub Actions"].required is False
    assert skills["Python"].required is True
