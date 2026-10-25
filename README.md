# SkillLens

SkillLens is a full-stack AI application that analyzes software-engineering job descriptions, extracts technical skills, compares them with a candidate's CV, and identifies skill gaps with personalized learning recommendations.

## Features

* AI-powered skill extraction from job descriptions
* PDF CV upload and text extraction
* Skill normalization and categorization
* Deterministic CV-to-job skill matching
* Explainable match score
* Required vs. preferred skill analysis
* AI-generated skill-gap recommendations
* Persistent job and CV data with PostgreSQL
* REST API built with FastAPI
* React + TypeScript frontend
* Dockerized development and deployment setup
* Automated tests with pytest
* Database migrations with Alembic

## Architecture

```text
                         SkillLens
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
       React + TypeScript            FastAPI API
              │                           │
              │ HTTP/JSON                 │
              └─────────────┬─────────────┘
                            │
                  ┌─────────┼─────────┐
                  │         │         │
                  ▼         ▼         ▼
               OpenAI   SQLAlchemy  PDF parser
                  │         │
                  │         ▼
                  │     PostgreSQL
                  │
                  ▼
          Structured skill data
                  │
                  ▼
        Deterministic match engine
                  │
                  ▼
          LLM recommendations
```

## Tech Stack

### Frontend

* React
* TypeScript
* Vite
* Nginx

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* pypdf

### AI

* OpenAI API
* Structured Outputs

### Database

* PostgreSQL

### Infrastructure

* Docker
* Docker Compose

### Testing

* pytest
* HTTPX

## Project Structure

```text
skilllens/
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── routers/
│   ├── services/
│   ├── tests/
│   ├── api_schemas.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

## Local Development

### Prerequisites

* Docker Desktop
* Python 3.14+
* uv
* Node.js 20+

### Environment Variables

Create `backend/.env` from `backend/.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_model

DATABASE_URL=postgresql+psycopg://jobfit:jobfit_dev_password@localhost:5432/jobfit
```

For the frontend, create `frontend/.env` from `frontend/.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

Never commit `.env` files or API keys.

### Start the application

From the project root:

```bash
docker compose up -d --build
```

Run the database migration:

```bash
cd backend
uv run alembic upgrade head
```

The services are then available at:

```text
Frontend:  http://localhost:3000
Backend:   http://localhost:8000
API docs:  http://localhost:8000/docs
```

## Running Tests

From `backend/`:

```bash
uv run pytest
```

## Database Migrations

Create a migration after changing the SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "describe your change"
```

Review the generated migration, then apply it:

```bash
uv run alembic upgrade head
```

## API

Main endpoints:

```text
POST /api/jobs
GET  /api/jobs
GET  /api/jobs/{job_id}

POST /api/resumes
GET  /api/resumes
GET  /api/resumes/{resume_id}

POST /api/matches

POST /api/recommendations
```

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

## Matching Approach

Skill matching is deliberately deterministic.

The application first normalizes skills such as:

```text
Postgres → PostgreSQL
REST APIs → REST API
k8s → Kubernetes
```

It then compares canonical job and CV skills.

Required skills receive a higher weight than preferred skills when calculating the match score.

AI is used for language-heavy tasks such as:

* extracting skills from unstructured text
* generating explanations
* generating personalized learning recommendations

This keeps the core matching logic predictable and testable.

## Current Limitations

* Text-based PDFs are supported; scanned PDFs requiring OCR are not yet supported.
* Authentication is not implemented yet.
* The current version is intended as a portfolio/demo application rather than a production service handling sensitive CV data at scale.
* Job-board scraping is not part of the current application.

## Roadmap

* User authentication
* Saved match history
* Better skill taxonomy
* Semantic skill matching
* OCR support for scanned CVs
* CI/CD with GitHub Actions
* Production deployment
* Improved analytics and job-market insights

## License

This project is currently intended as a personal portfolio project.
