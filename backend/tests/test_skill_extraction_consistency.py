from types import SimpleNamespace

from schemas import Skill, SkillExtractionResult
from services import skill_extractor


def make_result(skills):
    return SkillExtractionResult(
        skills=[
            Skill(
                name=name,
                category="Cloud" if name == "AWS" else "Other",
                required=required,
            )
            for name, required in skills
        ]
    )


def mock_openai(monkeypatch, results):
    calls = []

    def fake_parse(**kwargs):
        calls.append(kwargs)

        return SimpleNamespace(
            output_parsed=results[len(calls) - 1]
        )

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(parse=fake_parse)
    )

    monkeypatch.setattr(
        skill_extractor,
        "OpenAI",
        lambda: fake_client,
    )

    return calls


def test_preserves_llm_optional_classification(monkeypatch):
    description = (
        "Python, Java and Docker are required. "
        "Experience with AWS is a plus."
    )

    response = make_result([
        ("Python", True),
        ("Java", True),
        ("Docker", True),
        ("AWS", False),
    ])

    calls = mock_openai(monkeypatch, [response])

    result = skill_extractor.extract_skills(description)

    skills = {
        skill.name: skill.required
        for skill in result.skills
    }

    assert skills["Python"] is True
    assert skills["Java"] is True
    assert skills["Docker"] is True
    assert skills["AWS"] is False

    assert len(calls) == 1


def test_missing_skills_trigger_llm_retry(monkeypatch):
    description = (
        "Python, Java and Docker are required. "
        "Experience with AWS is a plus."
    )

    first_response = make_result([
        ("Python", True),
    ])

    second_response = make_result([
        ("Python", True),
        ("Java", True),
        ("Docker", True),
        ("AWS", False),
    ])

    calls = mock_openai(
        monkeypatch,
        [first_response, second_response],
    )

    result = skill_extractor.extract_skills(description)

    skills = {
        skill.name: skill.required
        for skill in result.skills
    }

    assert len(calls) == 2
    assert len(skills) == 4
    assert skills["AWS"] is False
    assert skills["Java"] is True


def test_does_not_invent_missing_skills(monkeypatch):
    description = (
        "Python, Java and Docker are required. "
        "Experience with AWS is a plus."
    )

    first_response = make_result([
        ("Python", True),
    ])

    second_response = make_result([
        ("Python", True),
        ("Java", True),
    ])

    calls = mock_openai(
        monkeypatch,
        [first_response, second_response],
    )

    result = skill_extractor.extract_skills(description)

    names = {skill.name for skill in result.skills}

    assert names == {"Python", "Java"}
    assert len(calls) == 2


def test_normalizes_duplicate_aliases(monkeypatch):
    description = "Experience with PostgreSQL is required."

    response = make_result([
        ("Postgres", True),
        ("PostgreSQL", True),
    ])

    calls = mock_openai(monkeypatch, [response])

    result = skill_extractor.extract_skills(description)

    assert len(result.skills) == 1
    assert result.skills[0].name == "PostgreSQL"
    assert len(calls) == 1
