# Aureon

AI-native, multi-agent Career Intelligence Platform. A central LangGraph
orchestrator dynamically routes between specialized agents (Discovery,
Career Intelligence, Decision, Skill Gap, Roadmap, Mentor, Institution,
Growth) to guide students from self-discovery to long-term career growth.
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design.

> **V1: Discovery Module** is implemented and live-verified against real
> Groq + Supabase — the conversational Discovery Agent, Why Engine,
> Exploration Mode, Reflection Journal, Career DNA, and Career Hypothesis
> Engine. The other 7 specialized agents remain honest no-op stubs
> (reachable by the orchestrator, not yet implemented). See
> `ARCHITECTURE.md` for the full design and what's still deferred.

## Prerequisites

- Python 3.11+
- Node.js 20+
- A Supabase project (URL + secret key)
- A Groq API key

## Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -e ".[dev]"
cp .env.example .env     # fill in real Supabase/Groq credentials
```

Run `db/migrations/0001_discovery_module.sql` once in your Supabase
project's SQL Editor (Project → SQL Editor → New query → paste → Run) to
create the `conversations`, `turns`, and `student_profiles` tables.

```bash
uvicorn aureon.main:app --reload
```

- API: http://localhost:8000
- Health check: http://localhost:8000/health
- Tests: `pytest`

## Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

- App: http://localhost:5173 — the Discovery conversation experience,
  with a live Discovery Notebook (Career DNA, hypotheses, reflection
  journal) alongside the chat.

## Project layout

```
Aureon/
├── backend/    Python / FastAPI / LangGraph — clean-architecture layers:
│               api/ (presentation) → domain/ (business logic) →
│               agents/ (multi-agent system) → services/ (LLM, Supabase)
├── frontend/   React / Vite / TypeScript / Tailwind
└── docs/       Architecture documentation
```
