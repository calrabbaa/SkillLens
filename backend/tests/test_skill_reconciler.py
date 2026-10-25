from schemas import Skill, SkillExtractionResult
from services.skill_reconciler import reconcile_skills


def test_preserves_optional_classification():
    description = (
        "Python and Java are required. "
        "Experience with AWS is a plus."
    )

    ai_result = SkillExtractionResult(
        skills=[
            Skill(
                name="Python",
                category="Programming",
                required=True,
            ),
            Skill(
                name="Java",
                category="Programming",
                required=True,
            ),
            Skill(
                name="AWS",
                category="Cloud",
                required=False,
            ),
        ]
    )

    result = reconcile_skills(description, ai_result)

    skills = {
        skill.name: skill.required
        for skill in result.skills
    }

    assert skills["Python"] is True
    assert skills["Java"] is True
    assert skills["AWS"] is False


def test_normalizes_and_deduplicates():
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

    result = reconcile_skills(
        "Experience with PostgreSQL.",
        ai_result,
    )

    assert len(result.skills) == 1
    assert result.skills[0].name == "PostgreSQL"


def test_does_not_invent_missing_skills():
    ai_result = SkillExtractionResult(
        skills=[
            Skill(
                name="Python",
                category="Programming",
                required=True,
            )
        ]
    )

    result = reconcile_skills(
        "Python, Java and Kotlin are required.",
        ai_result,
    )

    assert [skill.name for skill in result.skills] == ["Python"]
