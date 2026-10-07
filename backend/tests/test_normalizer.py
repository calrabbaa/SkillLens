from services.skill_normalizer import normalize_skill


def test_postgres_is_normalized_to_postgresql():
    name, category = normalize_skill(
        "Postgres",
        "Databases",
    )

    assert name == "PostgreSQL"
    assert category == "Databases"


def test_rest_apis_are_normalized_to_rest_api():
    name, category = normalize_skill(
        "REST APIs",
        "Backend",
    )

    assert name == "REST API"
    assert category == "Backend"


def test_k8s_is_normalized_to_kubernetes():
    name, category = normalize_skill(
        "k8s",
        "DevOps",
    )

    assert name == "Kubernetes"
    assert category == "DevOps"


def test_known_skill_gets_deterministic_category():
    name, category = normalize_skill(
        "Python",
        "Something invented by the LLM",
    )

    assert name == "Python"
    assert category == "Programming"


def test_unknown_skill_keeps_name_and_category():
    name, category = normalize_skill(
        "SomeObscureTool",
        "Other",
    )

    assert name == "SomeObscureTool"
    assert category == "Other"


def test_skill_name_whitespace_is_removed():
    name, category = normalize_skill(
        "  Python  ",
        "Programming",
    )

    assert name == "Python"
    assert category == "Programming"
