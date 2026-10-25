from services.match_engine import (
    JobSkillRequirement,
    Skill,
    calculate_skill_match,
)


def test_perfect_match():
    job_skills = [
        JobSkillRequirement(
            skill=Skill("Python", "Programming"),
            required=True,
        ),
        JobSkillRequirement(
            skill=Skill("Docker", "DevOps"),
            required=True,
        ),
        JobSkillRequirement(
            skill=Skill("AWS", "Cloud"),
            required=False,
        ),
    ]

    resume_skills = [
        Skill("Python", "Programming"),
        Skill("Docker", "DevOps"),
        Skill("AWS", "Cloud"),
    ]

    result = calculate_skill_match(
        job_skills,
        resume_skills,
    )

    assert result["overall_score"] == 100.0
    assert len(result["required_matched"]) == 2
    assert len(result["required_missing"]) == 0
    assert len(result["preferred_matched"]) == 1
    assert len(result["preferred_missing"]) == 0
    assert len(result["additional_resume_skills"]) == 0


def test_zero_match():
    job_skills = [
        JobSkillRequirement(
            skill=Skill("Python", "Programming"),
            required=True,
        ),
        JobSkillRequirement(
            skill=Skill("Docker", "DevOps"),
            required=True,
        ),
    ]

    resume_skills = [
        Skill("C++", "Programming"),
    ]

    result = calculate_skill_match(
        job_skills,
        resume_skills,
    )

    assert result["overall_score"] == 0.0
    assert len(result["required_matched"]) == 0
    assert len(result["required_missing"]) == 2
    assert len(result["additional_resume_skills"]) == 1


def test_required_skills_are_weighted_more_heavily():
    job_skills = [
        JobSkillRequirement(
            skill=Skill("Python", "Programming"),
            required=True,
        ),
        JobSkillRequirement(
            skill=Skill("Docker", "DevOps"),
            required=True,
        ),
        JobSkillRequirement(
            skill=Skill("React", "Frontend"),
            required=False,
        ),
    ]

    resume_skills = [
        Skill("Python", "Programming"),
        Skill("React", "Frontend"),
    ]

    result = calculate_skill_match(
        job_skills,
        resume_skills,
    )

    # Python = 2 weighted points
    # Docker = 0
    # React = 1
    #
    # Total = 5
    # Matched = 3
    # 3 / 5 = 60%

    assert result["overall_score"] == 60.0


def test_skill_matching_is_case_insensitive():
    job_skills = [
        JobSkillRequirement(
            skill=Skill("PostgreSQL", "Databases"),
            required=True,
        ),
    ]

    resume_skills = [
        Skill("postgresql", "Databases"),
    ]

    result = calculate_skill_match(
        job_skills,
        resume_skills,
    )

    assert result["overall_score"] == 100.0
    assert len(result["required_matched"]) == 1


def test_extra_resume_skills_are_identified():
    job_skills = [
        JobSkillRequirement(
            skill=Skill("Python", "Programming"),
            required=True,
        ),
    ]

    resume_skills = [
        Skill("Python", "Programming"),
        Skill("C++", "Programming"),
        Skill("Docker", "DevOps"),
    ]

    result = calculate_skill_match(
        job_skills,
        resume_skills,
    )

    assert result["overall_score"] == 100.0

    assert result["additional_resume_skills"] == [
        {
            "name": "C++",
            "category": "Programming",
        },
        {
            "name": "Docker",
            "category": "DevOps",
        },
    ]


def test_no_job_skills_returns_zero_score():
    result = calculate_skill_match(
        job_skills=[],
        resume_skills=[
            Skill("Python", "Programming"),
        ],
    )

    assert result["overall_score"] == 0.0
    assert result["required_matched"] == []
    assert result["required_missing"] == []
    assert result["preferred_matched"] == []
    assert result["preferred_missing"] == []

    assert result["additional_resume_skills"] == [
        {
            "name": "Python",
            "category": "Programming",
        }
    ]
