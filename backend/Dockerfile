FROM python:3.14-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /uvx /bin/

# Python/uv configuration.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_DEV=1

WORKDIR /app

# Copy dependency files first so Docker can cache dependency installation.
COPY pyproject.toml uv.lock ./

# Install production dependencies without installing the project itself.
RUN uv sync --locked --no-install-project

# Copy the application source code.
COPY . .

# Make the virtual environment's executables available directly.
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && fastapi run main.py --host 0.0.0.0 --port ${PORT:-8000}"]
