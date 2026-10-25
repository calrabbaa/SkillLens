from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from routers.jobs import router as jobs_router
from routers.resume import router as resumes_router
from routers.matches import router as matches_router
from routers.recommendations import router as recommendations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="SkillLens",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(jobs_router)
app.include_router(resumes_router)
app.include_router(matches_router)
app.include_router(recommendations_router)


class JobDescription(BaseModel):
    text: str = Field(min_length=20, max_length=50_000)


@app.get("/")
async def root():
    return {"message": "SkillLens API is running"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
