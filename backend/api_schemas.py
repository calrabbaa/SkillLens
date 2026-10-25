from datetime import datetime

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    description: str = Field(
        min_length=20,
        max_length=50_000,
    )


class SkillResponse(BaseModel):
    name: str
    category: str
    required: bool


class JobDetail(BaseModel):
    id: int
    description: str
    created_at: datetime
    skills: list[SkillResponse]


class JobSummary(BaseModel):
    id: int
    created_at: datetime
    skill_count: int


class ResumeSkillResponse(BaseModel):
    name: str
    category: str


class ResumeDetail(BaseModel):
    id: int
    filename: str
    created_at: datetime
    skills: list[ResumeSkillResponse]


class ResumeSummary(BaseModel):
    id: int
    filename: str
    created_at: datetime
    skill_count: int


class MatchSkill(BaseModel):
    name: str
    category: str


class MatchResult(BaseModel):
    job_id: int
    resume_id: int

    overall_score: float

    required_matched: list[MatchSkill]
    required_missing: list[MatchSkill]

    preferred_matched: list[MatchSkill]
    preferred_missing: list[MatchSkill]

    additional_resume_skills: list[MatchSkill]


class RecommendationItem(BaseModel):
    skill_name: str
    importance: str
    what_to_learn: str
    practice_project: str


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
