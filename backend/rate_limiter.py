from fastapi import Request
from slowapi import Limiter


def demo_limit_key(request: Request) -> str:
    # One shared budget for the entire public demo.
    return "skilllens-public-demo"


limiter = Limiter(key_func=demo_limit_key)

ai_rate_limit = limiter.shared_limit(
    "10/hour",
    scope="openai-requests",
)
