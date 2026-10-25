from services.skill_detector import detect_explicit_skills


def test_detects_explicit_technologies():
    description = """
    Experience with Python, FastAPI, React,
    TypeScript, PostgreSQL, Docker, and Git.
    """

    result = detect_explicit_skills(description)

    assert result == {
        "Python",
        "FastAPI",
        "React",
        "TypeScript",
        "PostgreSQL",
        "Docker",
        "Git",
    }


def test_detects_common_variations():
    description = """
    Experience with REST APIs, Postgres,
    GitHub Actions, and CI/CD.
    """

    result = detect_explicit_skills(description)

    assert {
        "REST API",
        "PostgreSQL",
        "GitHub Actions",
        "CI/CD",
    }.issubset(result)


def test_avoids_partial_word_matches():
    description = """
    We use GitHub and reactive programming.
    """

    result = detect_explicit_skills(description)

    assert "GitHub" in result
    assert "Git" not in result
    assert "React" not in result


def test_no_technical_skills():
    description = """
    We value teamwork, communication,
    motivation, and problem solving.
    """

    assert detect_explicit_skills(description) == set()
