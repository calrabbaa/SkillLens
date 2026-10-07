import os

from dotenv import load_dotenv
from openai import OpenAI

from schemas import SkillExtractionResult


load_dotenv()

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")


SYSTEM_PROMPT = """
You are a precise skill extraction system for software-engineering job
descriptions.

Your job is to identify EVERY distinct technical skill explicitly mentioned
in the job description.

IMPORTANT:
- Aim for completeness, not brevity.
- Do not stop after finding the first few skills.
- Extract all distinct technologies, programming languages, frameworks,
  libraries, databases, cloud platforms, DevOps tools, AI/ML technologies,
  security technologies, testing technologies, and technical tools mentioned.
- Extract skills even when they appear only once.
- Do not invent skills that are not supported by the text.
- Do not merge clearly distinct technologies into one skill.
- Use the most recognizable canonical name for each skill.

Examples:
- "Python and Java" → Python, Java
- "React and TypeScript" → React, TypeScript
- "PostgreSQL and SQL" → PostgreSQL, SQL
- "AWS and Docker" → AWS, Docker
- "PyTorch and TensorFlow" → PyTorch, TensorFlow
- "REST APIs" → REST API

REQUIRED STATUS:
- required=true when the wording indicates the employer expects or requires
  the skill.
- required=false only when it is explicitly described as optional, preferred,
  beneficial, desirable, or "a plus".
- If the description simply says that candidates should have experience with
  a skill without calling it optional, treat it as required.

CATEGORIES:
- Programming: programming languages such as Python, Java, C++, JavaScript
- Frontend: frontend frameworks and technologies such as React, Angular, Vue
- Backend: backend frameworks and server technologies such as FastAPI, Django,
  Spring
- Databases: SQL, PostgreSQL, MySQL, MongoDB and similar technologies
- DevOps: Docker, Kubernetes, CI/CD, Terraform and similar technologies
- Cloud: AWS, Azure, GCP and similar cloud platforms
- AI / ML: machine learning, deep learning, LLMs, RAG, PyTorch, TensorFlow,
  computer vision and similar technologies
- Security: cybersecurity, penetration testing, IAM, encryption and similar
  technologies
- Testing: unit testing, integration testing, test automation and QA tools
- Other: technical skills that do not fit the categories above

Do not include generic soft skills such as teamwork, motivation,
communication, flexibility, or problem solving.

Return every supported skill found in the job description.
"""


def extract_skills(job_description: str) -> SkillExtractionResult:
    response = client.responses.parse(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": job_description,
            },
        ],
        text_format=SkillExtractionResult,
    )

    if response.output_parsed is None:
        raise RuntimeError("The model did not return a structured result.")

    return response.output_parsed
