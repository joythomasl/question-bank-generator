# Question Bank Generator

An autonomous, machine-verified bank of interview questions — algorithmic
(with Python + Java solutions, 10 edge-case test cases each) and bonus
conceptual (OS / ML / DBMS / Networks) — scraped, tagged, generated, and
execution-verified on a recurring schedule with **zero manual curation
required**, browsable through a React portal with a user-facing catalog and
a separate admin panel.

```
pipeline/     scraping + tagging + LLM enrichment + execution-verification pipeline
backend/      FastAPI server — serves questions, runs the pipeline on a timer, admin edit/remove API
frontend/     React + Vite + Tailwind portal (user catalog + admin panel)
tests/        backend/pipeline test suite
docs/         original project plan / design rationale
```

---

## How it works

```
┌─────────────────────────────────────────────────────────────────────┐
│  PIPELINE (pipeline/)                                                │
│  scrape → deterministic tag → LLM/template enrich → verify → upsert  │
│                                                                        │
│  scrapers.py              pull raw problems from 5 sites             │
│  deterministic_tagger.py  category / difficulty / company tagging    │
│  enforce_10_cases_and_verify.py  generate 10 test cases + solutions  │
│  verify.py                 execute Python & Java solutions in a      │
│                             subprocess sandbox against every test    │
│                             case — only verified: true rows survive  │
│  db.py                     upsert into Supabase (or local JSON)      │
│  run_pipeline.py            orchestrates all of the above            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BACKEND (backend/main.py — FastAPI)                                 │
│  • Serves /api/questions, /api/stats, /api/companies, /api/export    │
│  • Reads from Supabase if configured, else from                      │
│    frontend/public/questions.json (local fallback)                   │
│  • Runs the pipeline automatically every 30 minutes in a background  │
│    thread, and exposes POST /api/pipeline/run to trigger on demand   │
│  • Admin edit/remove endpoints write straight to Supabase when       │
│    configured; otherwise to backend/admin_overrides.json, which is   │
│    re-applied on every read so curation is visible to ALL clients    │
│    (not just the admin's own browser / localStorage)                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FRONTEND (frontend/ — React + Vite + Tailwind)                      │
│  • Login gate → User portal or Admin portal                          │
│  • User portal: filter/search/sort, checkbox-select, JSON export,    │
│    company bar, difficulty gauge, light/dark theme                   │
│  • Admin portal: analytics dashboard, edit difficulty, remove        │
│    questions, trigger a manual pipeline run                          │
└─────────────────────────────────────────────────────────────────────┘
```

A GitHub Actions workflow (`.github/workflows/pipeline.yml`) also runs the
pipeline independently every 30 minutes via cron, so the catalog keeps
growing even when the backend isn't deployed anywhere.

### Data sources

Codeforces, CSES, GeeksforGeeks, HackerRank, and public LeetCode
company-wise problem CSVs — see [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)
for the full sourcing rationale, question schema, and known limitations.

---

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- (Optional) A free [Groq](https://console.groq.com/keys) API key — only
  needed if you want to *run the generation pipeline yourself*. Not needed
  to just browse the app; a pre-generated `questions.json` already ships
  in the repo.
- (Optional) A [Supabase](https://supabase.com) project — only needed for
  a real persistent database. Without it, the backend transparently falls
  back to the bundled `frontend/public/questions.json` file plus a local
  `admin_overrides.json` for admin edits.

---

## Quick start — run the app

This is the fastest path to a working app: it starts the FastAPI backend
and the Vite dev server together, and works with **zero configuration**
(no `.env`, no Supabase) because the backend falls back to the local
`questions.json` bundle.

```bash
cd frontend
npm install
pip install -r ../backend/requirements.txt
npm run dev
```

This runs two processes concurrently:

| Service | URL | What it serves |
|---|---|---|
| Vite frontend | http://localhost:5173 | The React portal (proxies `/api/*` to the backend) |
| FastAPI backend | http://127.0.0.1:8000 | REST API (docs at `/docs`) |

Open **http://localhost:5173** and choose **Continue as user** to browse,
or **Admin login** with password `admin123` (a demo-scale gate — see
[Notes on the admin password](#notes-on-the-admin-password) below).

If port 5173 is already in use, Vite will automatically pick the next
free port (5174, etc.) — watch the terminal output for the actual URL.

### Running frontend / backend separately

```bash
# Terminal 1 — backend only
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000

# Terminal 2 — frontend only
cd frontend
npm install
npm run dev:vite
```

### Configuring a real database (optional)

By default there's nothing to configure. To point the backend at a real
Supabase Postgres database instead of the local JSON fallback, create
`backend/.env` (or export the vars in your shell):

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_or_anon_key
```

Apply `pipeline/schema.sql` to your Supabase project first (creates the
`questions` and `pipeline_runs` tables). When these two vars are set, the
backend reads/writes Supabase directly and the local
`admin_overrides.json` layer is unused.

---

## Running the generation pipeline yourself

The repo ships with a pre-generated, pre-verified `questions.json`, so
this step is **only needed if you want to regenerate or extend the
question bank**.

```bash
cd pipeline
python -m venv venv && source venv/bin/activate   # or your preferred venv tool
pip install -r requirements.txt
cp .env.example .env      # then fill in GROQ_API_KEY (free tier, no card needed)

python run_pipeline.py
```

`run_pipeline.py` orchestrates the full chain: scrape → deterministic tag
→ LLM/template enrichment (10 test cases + Python/Java solutions) →
subprocess execution-verification → upsert. Only questions that pass
every generated test case in both Python and Java are kept.

You can also trigger a run without touching the pipeline directly:

- **On demand**, while the backend is running: `POST /api/pipeline/run`
  (also exposed as a button in the Admin portal)
- **Automatically**, every 30 minutes, via the backend's own background
  thread (starts once `uvicorn` boots) and independently via the
  `pipeline.yml` GitHub Actions cron job

Environment variables used by the pipeline:

| Variable | Required for | Notes |
|---|---|---|
| `GROQ_API_KEY` | LLM enrichment (`enrich.py`, `classify.py`) | Free tier, get one at console.groq.com/keys |
| `NVIDIA_API_KEY` | Fallback/alternate generation path | Optional |
| `SUPABASE_URL` / `SUPABASE_KEY` | Writing verified questions to a real DB | Optional — pipeline can also just refresh the local JSON |

---

## Running tests

```bash
python -m unittest discover tests
```

Covers the FastAPI endpoints (via `TestClient`), the deterministic
tagger's category/difficulty/company logic, upsert dedupe behavior, and
the Python solution-verification runner.

---

## Deploying

- **Frontend**: `npm run build` inside `frontend/` produces a static
  bundle in `frontend/dist/` — deploy to Vercel/Netlify. Set the deployed
  frontend's API base URL to point at wherever the backend is hosted.
- **Backend**: any Python host that can run `uvicorn backend.main:app`
  (Render, Railway, Fly.io, etc.). Set `SUPABASE_URL`/`SUPABASE_KEY` there
  for persistent storage — without them it'll serve whatever
  `questions.json` snapshot is baked into that deployment.
- **Pipeline**: keeps running for free on its own via the GitHub Actions
  cron job as long as `GROQ_API_KEY` (and `SUPABASE_URL`/`SUPABASE_KEY` if
  you want it writing to a real DB) are set as repo secrets.

---

## Notes on the admin password

`admin123`, hardcoded in `frontend/src/components/LoginPage.jsx`, is a
**demo-scale gate, not real authentication** — fine for a project with no
sensitive data behind it, but change it (or swap in real auth) before any
public deployment.

---

## Further reading

[docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) has the full original design
doc: detailed data-source rationale, the question JSON schema, the
verification gate design, tech stack choices and why the project is free
to run, and known/honest limitations (e.g. Codeforces questions mostly
lack a real company tag, since they were never asked in an actual
interview).
