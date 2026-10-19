# Auto-Apply: Production-Ready Agentic AI Job Application Platform

[![CI Pipeline](https://github.com/Ayush2412Rao/Auto-Apply/actions/workflows/ci.yml/badge.svg)](https://github.com/Ayush2412Rao/Auto-Apply/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg)](https://nextjs.org/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini%203.8%20Flash-4285F4.svg)](https://ai.google.dev/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange.svg)](https://www.trychroma.com/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-blue.svg)](https://langchain-ai.github.io/langgraph/)

An autonomous, agentic AI platform that continuously discovers job openings hourly via Apify, evaluates them against a verified candidate profile using ChromaDB semantic retrieval and Google Gemini, generates truthful ATS-friendly tailored resumes (PDF & DOCX) with deterministic anti-hallucination validation, and tracks submissions through a glassmorphism Next.js dashboard.

---

## Architecture Overview

```
                                  +-----------------------------------------------------------+
                                  |                    Hourly Scheduler                       |
                                  |               (APScheduler / Asia/Kolkata)                |
                                  +-----------------------------+-----------------------------+
                                                                |
                                                                v
                                          +---------------------------------------+
                                          |         Apify Job Discovery           |
                                          |   (LinkedIn, Indeed, Glassdoor Actors)|
                                          +---------------------+-----------------+
                                                                |
                                                                v
                                          +---------------------------------------+
                                          |       Normalization & Deduplication   |
                                          | (Canonical URL / Requisition / Hash)  |
                                          +---------------------+-----------------+
                                                                |
                                                                v
                                          +---------------------------------------+
                                          |        Hard Eligibility Filters       |
                                          |   (Location, Visa, Excluded Empl.)    |
                                          +---------------------+-----------------+
                                                                |
                                                                v
                                          +---------------------------------------+
                                          |          ChromaDB Retrieval           |
                                          |    (Relevant Profile & Experience)    |
                                          +---------------------+-----------------+
                                                                |
                                                                v
                                          +---------------------------------------+
                                          |          Gemini AI Matching           |
                                          |      (0-100 Score, Skill Coverage)    |
                                          +---------------------+-----------------+
                                                                |
                                                  [Match Score >= Threshold]
                                                                |
                                                                v
                                          +---------------------------------------+
                                          |      Gemini Resume Tailoring          |
                                          |     + Deterministic Validation        |
                                          |       (PDF & DOCX Generation)         |
                                          +---------------------+-----------------+
                                                                |
                                                                v
                                          +---------------------------------------+
                                          |       LangGraph Policy & Routing      |
                                          +---------------------+-----------------+
                                                                |
                                         +----------------------+----------------------+
                                         |                                             |
                               [Approval Required]                               [Auto Submit]
                                         |                                             |
                                         v                                             v
                             +-----------------------+                    +-------------------------+
                             | User Reviews in UI    |                    | Playwright Submission   |
                             | & Resumes Execution   |                    | & Verification          |
                             +-----------------------+                    +-------------------------+
                                         |                                             |
                                         +----------------------+----------------------+
                                                                |
                                                                v
                                          +---------------------------------------+
                                          |       Database Persistence &          |
                                          |        SMTP Alert Notification        |
                                          +---------------------------------------+
```

---

## Key Features

1. **Continuous Autonomous Discovery**: Hourly job collection via Apify actors with SHA-256 deduplication and canonical URL resolution.
2. **Two-Stage Intelligent Matching**:
   - *Stage 1 (Deterministic)*: Hard constraints on target roles, hybrid/remote locations, and excluded employers.
   - *Stage 2 (Semantic)*: Hybrid ChromaDB cosine similarity retrieval combined with Gemini evaluation rubric (0-100 score).
3. **Truthful Resume Tailoring Engine**:
   - Reorders and synthesizes verified achievements grounded in candidate profile.
   - **Deterministic Anti-Hallucination Validator**: Rigorously verifies all organizations, degree programs, and technical skills against ground truth. Prevents fabricated credentials.
   - Generates dual ATS-optimized formats: **PDF** (via ReportLab) and **DOCX** (via python-docx).
4. **LangGraph State Machine**: 6-node deterministic workflow supporting autonomous execution and human-in-the-loop review.
5. **Modern Glassmorphism UI (Next.js 14)**:
   - **Overview Dashboard**: Live statistics, scheduler status, manual agent trigger.
   - **Job Discovery Studio**: Searchable table, match score badges, missing qualification alerts.
   - **Resume Studio**: Master resume viewer, tailored versions, one-click PDF & DOCX downloads.
   - **Application Kanban**: Status columns (`Matched` → `Pending Approval` → `Submitting` → `Applied`).
   - **Live Agent Logs**: Audit timeline with step-by-step event stream.
   - **Settings**: Dynamic policy switching (`automatic` vs `approval_required`), threshold sliders.
6. **Dual Database Architecture**: SQLite for zero-setup local execution; PostgreSQL for production container deployment.

---

## Directory Structure

```text
Auto-Apply/
├── backend/
│   ├── app/
│   │   ├── agent/            # LangGraph workflow nodes, state, and graph
│   │   ├── ai/               # Gemini client, matcher, tailor, validator, document builder
│   │   ├── api/routes/       # FastAPI endpoints (health, jobs, profile, resumes, agent)
│   │   ├── db/               # SQLAlchemy engine, session factory, schema migrations
│   │   ├── discovery/        # Apify scraper client, normalizer, and deduplicator
│   │   ├── models/           # SQLAlchemy models (User, Job, Evaluation, Application, Resume)
│   │   ├── scheduler/        # APScheduler background runner (Asia/Kolkata timezone)
│   │   ├── vector_store/     # ChromaDB embedding & semantic retrieval service
│   │   ├── config.py         # Application settings & environment loader
│   │   └── main.py           # FastAPI entrypoint
│   └── Dockerfile            # Container build for backend
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router pages (jobs, resumes, applications, agent, settings)
│   │   ├── components/       # Header, Sidebar, modal components
│   │   └── lib/              # Axios API client, TypeScript definitions
│   └── Dockerfile            # Multi-stage production container build
├── data/
│   ├── master_profile.json   # Verified candidate profile
│   ├── preferences.json      # Job search & auto-apply preferences
│   ├── questionnaire_answers.json # Pre-verified application answers
│   └── resumes/              # Master and tailored resumes (PDF & DOCX)
├── tests/                    # Automated pytest suite (12 passed tests)
├── docker-compose.yml        # Full-stack Docker deployment orchestration
└── requirements.txt          # Python dependencies
```

---

## Quickstart

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Google Gemini API Key

### 2. Configure Environment
Create a `.env` file in the project root:
```env
APP_ENV=development
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///data/career_navigator.db

# AI & Apify
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
APIFY_API_TOKEN=your_apify_token_here

# Scheduler & Timezone
SCHEDULER_INTERVAL_HOURS=1
SCHEDULER_TIMEZONE=Asia/Kolkata

# Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_16_char_app_password
NOTIFICATION_EMAIL=your_email@gmail.com
```

### 3. Run Backend
```bash
# Activate virtual environment
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`

### 4. Run Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Testing

Run the automated test suite with full coverage:
```bash
.venv\Scripts\python.exe -m pytest tests -v
```
All 12 unit and integration tests validate:
- ✅ Healthcheck & API endpoints (`tests/test_api.py`)
- ✅ Normalization & deduplication schemas (`tests/test_discovery.py`)
- ✅ Hard filtering & Gemini semantic scoring (`tests/test_gemini_matching.py`)
- ✅ Anti-hallucination resume validator catching false claims (`tests/test_resume_validator.py`)

---

## Production Deployment with Docker Compose

To run the complete stack (PostgreSQL + FastAPI Backend + Background Scheduler + Next.js Dashboard):
```bash
docker compose up -d --build
```
Services exposed:
- **Frontend Dashboard**: `http://localhost:3000`
- **FastAPI Backend**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432`

---

*Maintained by [@Ayush2412Rao](https://github.com/Ayush2412Rao)*
