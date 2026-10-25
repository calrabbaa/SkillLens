from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import models
import pytest

from database import Base
from services.match_service import calculate_match


def create_test_database():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    return engine


def test_calculate_match():
    engine = create_test_database()

    with Session(engine) as db:
        python = models.Skill(
            name="Python",
            category="Programming",
        )

        docker = models.Skill(
            name="Docker",
            category="DevOps",
        )

        aws = models.Skill(
            name="AWS",
            category="Cloud",
        )

        cpp = models.Skill(
            name="C++",
            category="Programming",
        )

        db.add_all([
            python,
            docker,
            aws,
            cpp,
        ])

        db.flush()

        demo_session_id = "test-session-123"

        job = models.Job(
            description="Python Docker AWS job",
            demo_session_id=demo_session_id,
        )

        db.add(job)
        db.flush()

        db.add_all([
            models.JobSkill(
                job_id=job.id,
                skill_id=python.id,
                required=True,
            ),
            models.JobSkill(
                job_id=job.id,
                skill_id=docker.id,
                required=True,
            ),
            models.JobSkill(
                job_id=job.id,
                skill_id=aws.id,
                required=False,
            ),
        ])

        resume = models.Resume(
            filename="test-cv.pdf",
            extracted_text="Python AWS C++",
            demo_session_id=demo_session_id,
        )

        db.add(resume)
        db.flush()

        db.add_all([
            models.ResumeSkill(
                resume_id=resume.id,
                skill_id=python.id,
            ),
            models.ResumeSkill(
                resume_id=resume.id,
                skill_id=aws.id,
            ),
            models.ResumeSkill(
                resume_id=resume.id,
                skill_id=cpp.id,
            ),
        ])

        db.commit()

        result = calculate_match(
            db=db,
            job_id=job.id,
            resume_id=resume.id,
            demo_session_id=demo_session_id,
        )

    assert result["job_id"] == job.id
    assert result["resume_id"] == resume.id

    assert result["required_matched"] == [
        {
            "name": "Python",
            "category": "Programming",
        }
    ]

    assert result["required_missing"] == [
        {
            "name": "Docker",
            "category": "DevOps",
        }
    ]

    assert result["preferred_matched"] == [
        {
            "name": "AWS",
            "category": "Cloud",
        }
    ]

    assert result["preferred_missing"] == []

    assert result["additional_resume_skills"] == [
        {
            "name": "C++",
            "category": "Programming",
        }
    ]

    assert result["overall_score"] == 60.0

def test_calculate_match_rejects_other_sessions():
    engine = create_test_database()

    with Session(engine) as db:
        # Visitor A's records
        job_a = models.Job(
            description="Python developer position",
            demo_session_id="visitor-a",
        )
        resume_a = models.Resume(
            filename="a.pdf",
            extracted_text="Python developer",
            demo_session_id="visitor-a",
        )

        # Visitor B's records
        job_b = models.Job(
            description="Java developer position",
            demo_session_id="visitor-b",
        )
        resume_b = models.Resume(
            filename="b.pdf",
            extracted_text="Java developer",
            demo_session_id="visitor-b",
        )

        db.add_all([job_a, resume_a, job_b, resume_b])
        db.commit()

        # Visitor A cannot access Visitor B's job.
        with pytest.raises(ValueError, match="Job not found"):
            calculate_match(
                db=db,
                job_id=job_b.id,
                resume_id=resume_a.id,
                demo_session_id="visitor-a",
            )

        # Visitor A cannot access Visitor B's CV.
        with pytest.raises(ValueError, match="CV not found"):
            calculate_match(
                db=db,
                job_id=job_a.id,
                resume_id=resume_b.id,
                demo_session_id="visitor-a",
            )
