
# SkillLens

**AI-powered CV-to-job skill matching and personalized learning recommendations.**

SkillLens is a full-stack web application that helps software developers evaluate how well their technical skills match job requirements.

Users can upload a PDF CV, analyze a job description, identify matching and missing skills, and receive AI-generated learning recommendations with practical project ideas.

**[Try the Live Demo](https://skilllens.online)** · **[Explore the API](https://skilllens-api-amzw.onrender.com/docs)**

## Features

- **AI-powered skill extraction** — Analyze job descriptions and CVs using OpenAI Structured Outputs, with deterministic skill detection and normalization for more consistent results.
- **CV-to-job matching** — Calculate an explainable match score using deterministic matching logic that distinguishes required and preferred skills.
- **Skill-gap analysis** — Identify matching skills, missing requirements, and additional skills from the candidate's CV.
- **Personalized learning recommendations** — Generate actionable learning suggestions and practical portfolio project ideas.
- **Anonymous demo sessions** — Allow visitors to explore the application without registration while keeping their data isolated.
- **Privacy-focused CV handling** — Validate PDF uploads and automatically clean up stored CV data after a three-day retention threshold using scheduled daily deletion.

## Live Demo

**Website:** https://skilllens.online

Try SkillLens in three steps:

1. Upload a text-based PDF CV (maximum 5 MB and 4 pages).
2. Paste a software engineering job description.
3. Analyze the match and explore personalized learning recommendations.

> **Privacy note:** This is a public portfolio demo. Avoid uploading sensitive personal information. CV data is stored temporarily and scheduled for automatic deletion once it is older than three days.


## Architecture

SkillLens uses a decoupled frontend/backend architecture, with managed cloud infrastructure for deployment and persistent storage.

```mermaid
flowchart TD
    User["User / Browser"]

    subgraph Frontend["Frontend — Vercel"]
        React["React + TypeScript + Vite"]
    end

    subgraph Backend["Backend — Render"]
        API["FastAPI REST API"]
        Sessions["Anonymous Session Validation"]
        Extractor["Hybrid Skill Extraction"]
        Matcher["Deterministic Matching Engine"]
        PDF["PDF Processing"]
        Recommendations["AI Recommendations"]
    end

    subgraph External["External Services"]
        DB[("Supabase PostgreSQL")]
        OpenAI["OpenAI API"]
        Cron["Supabase Cron"]
    end

    User --> React
    React -->|"HTTPS / JSON"| API

    API --> Sessions
    API --> PDF
    API --> Extractor
    API --> Matcher
    API --> Recommendations

    Extractor --> OpenAI
    Recommendations --> OpenAI

    API <-->|"SQLAlchemy"| DB
    Cron -->|"Scheduled CV cleanup"| DB
```

### Key Design Decisions

- **Separation of concerns:** The React frontend communicates with FastAPI through REST endpoints, allowing independent deployment and development.
- **Hybrid AI extraction:** OpenAI Structured Outputs are combined with deterministic technology detection, normalization, and deduplication for more consistent results.
- **Deterministic matching:** The match score is calculated from normalized skills rather than generated directly by an LLM.
- **Anonymous sessions:** Signed session tokens provide session-level data isolation without requiring user registration.
- **Privacy and abuse protection:** PDF validation, AI request rate limiting, and scheduled CV deletion help protect the public demo.
- **Automated deployment:** GitHub Actions runs backend tests, while Render and Vercel deploy changes from the GitHub repository.


## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite, CSS |
| Backend | Python 3.14, FastAPI, Pydantic |
| AI | OpenAI API, Structured Outputs, deterministic skill detection |
| Database | PostgreSQL, SQLAlchemy, Psycopg 3 |
| Migrations | Alembic |
| PDF Processing | pypdf |
| Security | itsdangerous (signed sessions), SlowAPI (rate limiting), CORS |
| Testing | pytest, HTTPX |
| Development | Docker, Docker Compose, uv, npm |
| CI/CD | GitHub Actions, Render, Vercel |
| Cloud Services | Supabase PostgreSQL, Supabase Cron, OpenAI API |

### Deployment

| Component | Platform |
|---|---|
| Frontend | Vercel |
| Backend API | Render |
| PostgreSQL Database | Supabase |
| Scheduled CV Cleanup | Supabase Cron |
| Automated Backend Tests | GitHub Actions |

The frontend and backend are independently deployed. Docker Compose provides a reproducible local development environment.


## Project Structure

```text
SkillLens/
├── .github/
│   └── workflows/
│       └── backend-tests.yml       # CI testing
│
├── backend/
│   ├── alembic/
│   │   └── versions/               # Database migrations
│   ├── routers/                    # REST API endpoints
│   ├── services/                   # Business logic
│   │   ├── skill_extractor.py      # OpenAI skill extraction
│   │   ├── skill_detector.py       # Explicit skill detection
│   │   ├── skill_reconciler.py     # Extraction reconciliation
│   │   ├── skill_normalizer.py     # Canonical skill names
│   │   ├── match_service.py        # Deterministic matching
│   │   └── pdf_extractor.py        # PDF text extraction
│   │
│   ├── tests/                      # Unit and API tests
│   ├── main.py                     # FastAPI application
│   ├── models.py                   # SQLAlchemy models
│   ├── schemas.py                  # Data validation schemas
│   ├── database.py                 # Database configuration
│   ├── demo_sessions.py            # Signed anonymous sessions
│   ├── rate_limiter.py             # AI request limits
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Application dashboard
│   │   ├── api.ts                  # API client and session handling
│   │   └── index.css               # Application styling
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml              # Local development services
└── README.md
```

### Backend Organization

The backend follows a layered structure:

- **Routers:** Handle HTTP requests, input validation, and session authorization.
- **Services:** Implement PDF processing, skill extraction, matching, and recommendations.
- **Models:** Define PostgreSQL tables and relationships through SQLAlchemy.
- **Schemas:** Validate structured API and AI responses.
- **Tests:** Verify matching, skill extraction, security rules, and API behavior.


## Local Development

### Prerequisites

- Docker Desktop with Docker Compose
- An OpenAI API key with available API credits

Python 3.14, [uv](https://docs.astral.sh/uv/), and Node.js are only required when running the backend or frontend tools outside Docker.

### 1. Clone the Repository

```bash
git clone https://github.com/calrabbaa/SkillLens.git
cd SkillLens
```

### 2. Configure Environment Variables

Copy the example backend environment file:

```bash
cp backend/.env.example backend/.env
```

On Windows PowerShell, use `Copy-Item` instead of `cp` if preferred.

Edit `backend/.env` and configure:

```dotenv
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_model
DEMO_SESSION_SECRET=your_secure_random_secret

DATABASE_URL=postgresql+psycopg://skilllens:skilllens_dev_password@localhost:5432/skilllens
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Generate a secure session secret with Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Never commit `.env` files or expose API keys and session secrets.**

Docker Compose overrides `DATABASE_URL` inside the backend container to connect to the local PostgreSQL service.

The frontend API address is configured through the Docker build argument in `docker-compose.yml`.

### 3. Start the Application

From the repository root:

```bash
docker compose up -d --build
```

This starts three services:

- PostgreSQL database
- FastAPI backend
- React frontend served through Nginx

The backend automatically applies Alembic migrations during startup.

### 4. Access SkillLens

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Documentation | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |

The frontend automatically creates an anonymous demo session when needed.

### 5. Stop the Application

```bash
docker compose down
```

To rebuild after making changes:

```bash
docker compose up -d --build
```

**Note:** Running `docker compose down -v` also deletes the local PostgreSQL volume and its data.


## API

SkillLens exposes a REST API through FastAPI.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/demo-session` | Create an anonymous demo session |
| GET | `/api/health` | Check API health |
| POST | `/api/jobs` | Analyze and save a job description |
| GET | `/api/jobs` | List jobs belonging to the current session |
| GET | `/api/jobs/{job_id}` | Retrieve a job and its extracted skills |
| POST | `/api/resumes` | Upload and analyze a PDF CV |
| GET | `/api/resumes` | List CVs belonging to the current session |
| GET | `/api/resumes/{resume_id}` | Retrieve extracted CV skills |
| POST | `/api/matches` | Calculate a CV-to-job skill match |
| POST | `/api/recommendations` | Generate personalized learning recommendations |

### Authentication

SkillLens uses signed anonymous session tokens instead of user accounts.

First request a session:

```http
POST /api/demo-session
```

The response contains a signed token. Include it in subsequent protected API requests:

```http
Authorization: Bearer <session_token>
```

Session tokens expire after seven days.

### Rate Limiting

AI-powered endpoints share a demo-wide limit of 10 requests per hour. Exceeding the allowance returns HTTP `429 Too Many Requests`.

### Interactive Documentation

FastAPI provides automatically generated Swagger documentation:

- Local: http://localhost:8000/docs
- Production: https://skilllens-api-amzw.onrender.com/docs


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
