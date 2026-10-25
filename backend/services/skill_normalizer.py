import re


# Maps alternative names to one canonical skill name.
SKILL_ALIASES = {
    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgres db": "PostgreSQL",
    "postgres database": "PostgreSQL",

    "mysql": "MySQL",
    "my sql": "MySQL",

    # APIs
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",

    # Programming languages
    "python 3": "Python",
    "python3": "Python",

    "js": "JavaScript",
    "javascript": "JavaScript",

    "ts": "TypeScript",
    "typescript": "TypeScript",

    # Machine learning
    "ml": "Machine Learning",
    "machine-learning": "Machine Learning",

    # Common naming variations
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",

    "aws": "AWS",
    "amazon web services": "AWS",

    "gcp": "GCP",
    "google cloud": "GCP",

    "azure": "Azure",

    "pytorch": "PyTorch",
    "tensor flow": "TensorFlow",
    "tensorflow": "TensorFlow",

    "llms": "LLM",
    "large language models": "LLM",
    "large language model": "LLM",

    "openai api": "OpenAI",
}


# Deterministic categories for skills we explicitly recognize.
SKILL_CATEGORIES = {
    "Python": "Programming",
    "Java": "Programming",
    "C++": "Programming",
    "C#": "Programming",
    "JavaScript": "Programming",
    "TypeScript": "Programming",

    "React": "Frontend",
    "Angular": "Frontend",
    "Vue": "Frontend",

    "FastAPI": "Backend",
    "Django": "Backend",
    "Spring": "Backend",
    "REST API": "Backend",

    "SQL": "Databases",
    "PostgreSQL": "Databases",
    "MySQL": "Databases",

    "Docker": "DevOps",
    "Kubernetes": "DevOps",

    "AWS": "Cloud",
    "Azure": "Cloud",
    "GCP": "Cloud",

    "PyTorch": "AI / ML",
    "TensorFlow": "AI / ML",
    "Machine Learning": "AI / ML",
    "Deep Learning": "AI / ML",
    "LLM": "AI / ML",
    "RAG": "AI / ML",
    "OpenAI": "AI / ML",
}


def normalize_key(value: str) -> str:
    """
    Convert a skill name into a simple lookup key.

    Examples:
        "  Postgres  " -> "postgres"
        "REST APIs"   -> "rest apis"
        "Python 3"    -> "python 3"
    """
    value = value.strip().casefold()
    value = re.sub(r"[\s_-]+", " ", value)

    return value


def normalize_skill(
    name: str,
    category: str,
) -> tuple[str, str]:
    """
    Return a canonical skill name and category.

    Known skills use our deterministic taxonomy.
    Unknown skills keep the LLM-provided category.
    """

    lookup_key = normalize_key(name)

    canonical_name = SKILL_ALIASES.get(
        lookup_key,
        name.strip(),
    )

    canonical_category = SKILL_CATEGORIES.get(
        canonical_name,
        category,
    )

    return canonical_name, canonical_category
