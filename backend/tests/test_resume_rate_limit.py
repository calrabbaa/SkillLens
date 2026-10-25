from datetime import datetime, timezone

from fastapi.testclient import TestClient

from database import get_db
from demo_sessions import get_demo_session_id
from main import app
from rate_limiter import limiter

import routers.resume as resume_router


def test_resume_upload_rate_limit(monkeypatch):
    limiter.limiter.storage.reset()

    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_demo_session_id] = (
        lambda: "test-session"
    )

    monkeypatch.setattr(
        resume_router,
        "create_resume",
        lambda **kwargs: 123,
    )

    monkeypatch.setattr(
        resume_router,
        "get_resume_detail",
        lambda *args: {
            "id": 123,
            "filename": "test.pdf",
            "created_at": datetime.now(timezone.utc),
            "skills": [],
        },
    )

    try:
        with TestClient(app) as client:
            responses = []

            for _ in range(11):
                response = client.post(
                    "/api/resumes",
                    files={
                        "file": (
                            "test.pdf",
                            b"%PDF-1.4\n%%EOF",
                            "application/pdf",
                        )
                    },
                )
                responses.append(response.status_code)

        assert responses[:10] == [201] * 10
        assert responses[10] == 429

    finally:
        app.dependency_overrides.clear()
        limiter.limiter.storage.reset()
