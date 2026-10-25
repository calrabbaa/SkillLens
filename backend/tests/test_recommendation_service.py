from services.recommendation_service import (
    generate_recommendations,
)


def test_no_missing_skills_returns_empty_recommendations():
    result = generate_recommendations(
        job_description="Python developer",
        missing_skills=[],
    )

    assert result.recommendations == []
