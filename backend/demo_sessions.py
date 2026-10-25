import os
import secrets

from fastapi import Header, HTTPException
from itsdangerous import BadSignature, URLSafeTimedSerializer

SESSION_MAX_AGE = 7 * 24 * 60 * 60  # 7 days


def get_serializer() -> URLSafeTimedSerializer:
    secret = os.getenv("DEMO_SESSION_SECRET")

    if not secret:
        raise RuntimeError(
            "DEMO_SESSION_SECRET is not configured."
        )

    return URLSafeTimedSerializer(
        secret_key=secret,
        salt="skilllens-demo-session-v1",
    )


def create_demo_session() -> str:
    session_id = secrets.token_urlsafe(24)

    return get_serializer().dumps({
        "session_id": session_id,
    })


def get_demo_session_id(
    authorization: str | None = Header(default=None),
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing demo session token.",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = get_serializer().loads(
            token,
            max_age=SESSION_MAX_AGE,
        )
    except BadSignature:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired demo session.",
        )

    if not isinstance(payload, dict):
        raise HTTPException(status_code=401, detail="Invalid session.")

    session_id = payload.get("session_id")

    if not isinstance(session_id, str) or len(session_id) != 32:
        raise HTTPException(status_code=401, detail="Invalid session.")

    return session_id
