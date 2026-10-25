import re


SKILL_PATTERNS = {
    "Python": r"python(?:\s*3)?",
    "Java": r"java",
    "JavaScript": r"javascript",
    "TypeScript": r"typescript",
    "C++": r"c\+\+",
    "C#": r"c#",

    "React": r"react(?:\.js)?",
    "Angular": r"angular",
    "Vue": r"vue(?:\.js)?",

    "FastAPI": r"fastapi",
    "Django": r"django",
    "Spring Boot": r"spring\s+boot",

    "SQL": r"sql",
    "PostgreSQL": r"postgres(?:ql)?",
    "MySQL": r"mysql",
    "MongoDB": r"mongodb",

    "Docker": r"docker",
    "Kubernetes": r"kubernetes|k8s",
    "Git": r"git",
    "GitHub": r"github",
    "GitHub Actions": r"github\s+actions",
    "CI/CD": r"ci\s*/\s*cd",

    "REST API": r"rest(?:ful)?\s+apis?",
    "pytest": r"pytest",
    "Automated Testing": r"automated\s+testing",
    "Unit Testing": r"unit\s+testing",

    "AWS": r"aws|amazon\s+web\s+services",
    "Azure": r"azure",
    "GCP": r"gcp|google\s+cloud",

    "PyTorch": r"pytorch",
    "TensorFlow": r"tensorflow",
}


def detect_explicit_skills(text: str) -> set[str]:
    """
    Detect explicitly mentioned technical skills.

    Returns canonical skill names.
    Does not infer skills that aren't mentioned.
    """

    detected = set()

    for skill_name, pattern in SKILL_PATTERNS.items():
        regex = rf"(?<![A-Za-z0-9])(?:{pattern})(?![A-Za-z0-9])"

        if re.search(regex, text, re.IGNORECASE):
            detected.add(skill_name)

    return detected
