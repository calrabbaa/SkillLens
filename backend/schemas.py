from typing import Literal

from pydantic import BaseModel, Field


SkillCategory = Literal[
    "Programming",
    "Frontend",
    "Backend",
    "Databases",
    "DevOps",
    "Cloud",
    "AI / ML",
    "Security",
    "Testing",
    "Other",
]


class Skill(BaseModel):
    name: str = Field(
        description="The canonical name of a specific technical skill, "
        "technology, tool, framework, programming language, or platform."
    )
    category: SkillCategory = Field(
        description="The category that best describes the skill."
    )
    required: bool = Field(
        description="True when the job requires or expects the skill. "
        "False only when the job explicitly presents it as optional, "
        "preferred, beneficial, or a plus."
    )


class SkillExtractionResult(BaseModel):
    skills: list[Skill]


class SkillRecommendation(BaseModel):
    skill_name: str = Field(
        description="Canonical name of the missing skill."
    )

    importance: str = Field(
        description="Explain briefly why this skill matters for the target role."
    )

    what_to_learn: str = Field(
        description="Specific topics or concepts the candidate should learn."
    )

    practice_project: str = Field(
        description="A small practical project or exercise the candidate can build."
    )


class RecommendationResult(BaseModel):
    recommendations: list[SkillRecommendation]
