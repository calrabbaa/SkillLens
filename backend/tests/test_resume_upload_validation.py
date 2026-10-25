from fastapi.testclient import TestClient

from database import get_db
from demo_sessions import get_demo_session_id
from main import app
from rate_limiter import limiter

import routers.resume as resume_router


def test_upload_validation(monkeypatch):
    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_demo_session_id] = (
        lambda: "test-session"
    )

    def unexpected_processing(**kwargs):
        raise AssertionError(
            "Invalid uploads must not reach CV processing."
        )

    monkeypatch.setattr(
        resume_router,
        "create_resume",
        unexpected_processing,
    )

    limiter.limiter.storage.reset()

    try:
        with TestClient(app) as client:

            # PDF larger than 5 MB
            oversized = (
                b"%PDF" +
                b"x" * (resume_router.MAX_FILE_SIZE - 3)
            )

            response = client.post(
                "/api/resumes",
                files={
                    "file": (
                        "large.pdf",
                        oversized,
                        "application/pdf",
                    )
                },
            )
            assert response.status_code == 413

            # Empty PDF
            response = client.post(
                "/api/resumes",
                files={
                    "file": (
                        "empty.pdf",
                        b"",
                        "application/pdf",
                    )
                },
            )
            assert response.status_code == 400

            # Non-PDF content disguised as a PDF
            response = client.post(
                "/api/resumes",
                files={
                    "file": (
                        "fake.pdf",
                        b"This is not a PDF",
                        "application/pdf",
                    )
                },
            )
            assert response.status_code == 400

    finally:
        app.dependency_overrides.clear()
        limiter.limiter.storage.reset()
