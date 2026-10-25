import os

from dotenv import load_dotenv
from openai import OpenAI

from schemas import SkillExtractionResult

from services.skill_detector import detect_explicit_skills
from services.skill_normalizer import normalize_skill

from services.skill_reconciler import reconcile_skills

load_dotenv()

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
- Interpret required versus optional status using the full context
  and meaning of the job description, not only section headings.
- Understand equivalent expressions of preference or optionality,
  including "is a plus", "would be advantageous", and
  "not mandatory".
- Classify each skill individually, even when required and
  optional skills appear in the same sentence.

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
    client = OpenAI()

    def call_model(
        additional_instruction: str = "",
    ) -> SkillExtractionResult:

        user_content = job_description

        if additional_instruction:
            user_content += (
                "\n\nADDITIONAL REVIEW INSTRUCTIONS:\n"
                + additional_instruction
            )

        response = client.responses.parse(
            model=MODEL,
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
            text_format=SkillExtractionResult,
        )

        if response.output_parsed is None:
            raise RuntimeError(
                "The model did not return a structured result."
            )

        return reconcile_skills(
            job_description,
            response.output_parsed,
        )

    def normalized_names(
        result: SkillExtractionResult,
    ) -> set[str]:

        return {
            normalize_skill(
                skill.name,
                skill.category,
            )[0].casefold()
            for skill in result.skills
        }

    # First LLM extraction
    result = call_model()

    # Detect potential omissions, not requirements.
    expected = {
        normalize_skill(name, "Other")[0].casefold(): name
        for name in detect_explicit_skills(job_description)
    }

    extracted = normalized_names(result)

    missing = {
        canonical: name
        for canonical, name in expected.items()
        if canonical not in extracted
    }

    # Retry only when there are substantial omissions.
    if len(expected) >= 4 and len(missing) >= 2:

        retry_instruction = (
            "Review your previous extraction carefully.\n\n"
            "Previously identified skills:\n"
            + ", ".join(
                skill.name for skill in result.skills
            )
            + "\n\nPotentially overlooked technologies:\n"
            + ", ".join(sorted(missing.values()))
            + "\n\n"
            "Return a complete revised list of technical skills. "
            "Preserve previously identified skills if supported "
            "by the description, and include overlooked skills "
            "only when genuinely mentioned.\n\n"
            "Independently determine whether EACH skill is "
            "required or optional using the full semantic "
            "context of the original description. "
            "Do not assume that every skill is required."
        )

        retry_result = call_model(retry_instruction)

        # Compare coverage of explicitly detected skills.
        original_coverage = len(
            set(expected) & extracted
        )

        retry_coverage = len(
            set(expected) & normalized_names(retry_result)
        )

        if retry_coverage > original_coverage:
            result = retry_result

    return result
