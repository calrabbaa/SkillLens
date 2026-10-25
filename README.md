
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

## Screenshots

### Dashboard
Upload a CV, analyze job descriptions, and explore extracted technical skills.

![SkillLens Dashboard](docs/screenshots/dashboard.png)

### Skill Matching
Compare required and preferred skills with an explainable match score.

![Skill Matching Results](docs/screenshots/skill-matching.png)

### Personalized Learning Roadmap
Explore AI-generated recommendations and practical project ideas.

![Learning Recommendations](docs/screenshots/recommendations.png)



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
        Extractor["LLM-first Skill Extraction"]
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
- **LLM-first skill extraction:** SkillLens uses LLM-based semantic skill extraction with deterministic normalization, deduplication, completeness checks, and bounded retries. The LLM interprets whether each skill is required or optional based on the job description's context.
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
Replace OPENAI_MODEL with a model ID supported by your OpenAI API project. The selected model must support Structured Outputs.

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

## Running Tests

The backend includes automated tests covering skill extraction, matching logic, API validation, session isolation, rate limiting, and PDF processing.

Run the complete backend test suite:

```bash
cd backend
uv run pytest -v
```

Run the frontend production build:

```bash
cd ../frontend
npm ci
npm run build
```

Backend tests run automatically through GitHub Actions when changes are pushed to the repository.


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

SkillLens separates **AI-powered skill extraction** from **deterministic skill matching** to combine natural-language understanding with predictable, explainable results.

### 1. Skill Extraction

Job descriptions are analyzed using OpenAI Structured Outputs. The LLM identifies technical skills and determines whether each skill is **required** or **preferred**, based on the context of the job description.

To improve consistency, SkillLens applies:

- **Normalization:** Map different names for the same technology to a canonical representation.
- **Deduplication:** Remove duplicate skills and aliases.
- **Completeness checks:** Detect explicitly mentioned technologies that may have been overlooked.
- **Bounded retries:** Request an additional LLM extraction when substantial omissions are detected.

The deterministic checks do not override the LLM's required/optional classifications.

### 2. Skill Normalization

Before matching, equivalent skill names are mapped to canonical representations.

Examples:

```text
Postgres  → PostgreSQL
REST APIs → REST API
k8s       → Kubernetes
```

This reduces mismatches caused by differences in terminology.

### 3. Deterministic Skill Matching

After extraction and normalization, SkillLens compares the job's required and preferred skills against the skills extracted from the candidate's CV.

The matching engine:

- Identifies matched and missing skills.
- Assigns higher importance to required skills than preferred skills.
- Calculates a reproducible match score without asking an LLM to generate the score.

### Why This Approach?

LLMs are useful for interpreting unstructured language and understanding contextual requirements, while deterministic algorithms are better suited to consistent calculations.

By separating these responsibilities, SkillLens provides context-aware skill extraction alongside transparent and testable matching logic.


## Current Limitations

SkillLens is a portfolio demonstration, not a production-grade recruitment platform.

- **PDF support:** Only text-based PDFs are supported. Scanned documents requiring OCR are not supported. Uploads are limited to 5 MB, 4 pages, and 20,000 extracted characters.
- **Anonymous sessions:** Visitors can use the application without registration. Sessions expire after 7 days, and session data is not synchronized between devices.
- **Temporary CV storage:** CV data is automatically cleaned up once it is older than three days, with cleanup running daily. Because sessions last seven days, visitors may need to upload their CV again during an existing session.
- **AI variability:** Skill extraction and learning recommendations use an LLM. Results may vary, and extracted skills or classifications are not guaranteed to be perfect.
- **Rate limiting:** AI-powered endpoints share a limit of 10 requests per hour. Counters are currently stored in memory and reset when the backend restarts.
- **Skill matching:** Matching uses normalized skill names rather than semantic similarity, so related but differently named skills may not always match.
- **Security:** Session isolation, input validation, and rate limiting are implemented, but the application has not undergone a comprehensive security assessment.

The application is intended to demonstrate full-stack development, AI integration, database design, testing, and cloud deployment.


## Future Improvements

Potential improvements include:

- **Semantic skill matching:** Recognize related technologies and transferable skills beyond exact normalized names.
- **Persistent rate limiting:** Use shared storage to maintain request limits across backend restarts and multiple instances.
- **User accounts:** Add optional authentication and persistent user profiles.
- **OCR support:** Extract text from scanned CVs and image-based PDFs.
- **Skill taxonomy:** Improve canonicalization, categorization, and relationships between technologies.
- **Job-market insights:** Analyze recurring skill requirements across job postings.
- **Match history:** Allow users to track their skill development over time.

These features are potential extensions rather than requirements for the current portfolio demo.


## License

Copyright © 2026. All rights reserved.

This project is publicly available for portfolio and demonstration purposes.
