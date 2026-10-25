from types import SimpleNamespace

from schemas import Skill, SkillExtractionResult
from services import skill_extractor


def make_result(names):
    return SkillExtractionResult(
        skills=[
            Skill(
                name=name,
                category="Other",
                required=True,
            )
            for name in names
        ]
    )


def mock_openai(monkeypatch, results):
    """Replace OpenAI with predetermined responses."""
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


def test_incomplete_extraction_is_recovered(monkeypatch):
    description = """
    Requirements:
    Python, FastAPI, React, TypeScript,
    PostgreSQL, Docker, Git.

    Nice to have:
    GitHub Actions.
    """

    # First AI response contains just one skill.
    first_response = make_result(["Python"])

    # Retry improves the response but still misses skills.
    second_response = make_result([
        "Python",
        "FastAPI",
        "Docker",
    ])

    calls = mock_openai(
        monkeypatch,
        [first_response, second_response],
    )

    result = skill_extractor.extract_skills(description)

    names = {skill.name for skill in result.skills}

    expected = {
        "Python",
        "FastAPI",
        "React",
        "TypeScript",
        "PostgreSQL",
        "Docker",
        "Git",
        "GitHub Actions",
    }

    assert expected.issubset(names)

    # Incomplete extraction triggered exactly one retry.
    assert len(calls) == 2

    # Confirm that optional skills remain optional.
    skills = {skill.name: skill for skill in result.skills}

    assert skills["GitHub Actions"].required is False


def test_complete_extraction_does_not_retry(monkeypatch):
    description = """
    Requirements:
    Python, FastAPI, Docker, PostgreSQL.
    """

    complete_response = make_result([
        "Python",
        "FastAPI",
        "Docker",
        "PostgreSQL",
    ])

    calls = mock_openai(
        monkeypatch,
        [complete_response],
    )

    result = skill_extractor.extract_skills(description)

    names = {skill.name for skill in result.skills}

    assert names == {
        "Python",
        "FastAPI",
        "Docker",
        "PostgreSQL",
    }

    # No unnecessary second OpenAI request.
    assert len(calls) == 1
