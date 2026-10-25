import os

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from demo_sessions import create_demo_session
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from routers.jobs import router as jobs_router
from routers.resume import router as resumes_router
from routers.matches import router as matches_router
from routers.recommendations import router as recommendations_router

from dotenv import load_dotenv

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from rate_limiter import limiter

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="SkillLens",
    lifespan=lifespan,
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,https://skilllens.online",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(jobs_router)
app.include_router(resumes_router)
app.include_router(matches_router)
app.include_router(recommendations_router)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


class JobDescription(BaseModel):
    text: str = Field(min_length=20, max_length=50_000)


@app.get("/")
async def root():
    return {"message": "SkillLens API is running"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/demo-session", status_code=201)
def issue_demo_session(response: Response):
    response.headers["Cache-Control"] = "no-store"

    return {
        "token": create_demo_session(),
        "expires_in_seconds": 604800,
    }
