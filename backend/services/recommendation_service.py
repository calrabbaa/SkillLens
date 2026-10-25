import os

from dotenv import load_dotenv
from openai import OpenAI

from schemas import RecommendationResult


load_dotenv()

client = OpenAI()

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)


SYSTEM_PROMPT = """
You are a career-development assistant for software engineering students.

You receive a list of technical skills that are missing from a candidate's CV
relative to a specific job description.

For each missing skill:

1. Explain briefly why the skill matters for this particular job.
2. Suggest concrete topics the candidate should learn.
3. Suggest one small practical project or exercise that would let the
   candidate demonstrate the skill.

Rules:
- Only discuss skills provided in the missing-skills list.
- Do not invent additional skill gaps.
- Keep recommendations practical and achievable for a university student.
- Prefer concrete technologies, concepts, and exercises over vague advice.
- Tailor recommendations to the target job description when useful.
- Do not claim the candidate is unqualified.
- Do not repeat the entire job description.
- Keep each recommendation concise.
"""


def generate_recommendations(
    job_description: str,
    missing_skills: list[dict],
) -> RecommendationResult:

    if not missing_skills:
        return RecommendationResult(
            recommendations=[]
        )

    missing_skill_names = [
        skill["name"]
        for skill in missing_skills
    ]

    response = client.responses.parse(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Target job description:\n\n"
                    f"{job_description}\n\n"
                    "Missing skills:\n\n"
                    + "\n".join(
                        f"- {skill_name}"
                        for skill_name in missing_skill_names
                    )
                ),
            },
        ],
        text_format=RecommendationResult,
    )

    if response.output_parsed is None:
        raise RuntimeError(
            "The model did not return structured recommendations."
        )

    return response.output_parsed
