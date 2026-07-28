"""
main.py — FastAPI Backend Server for Question Bank Generator

Provides REST API endpoints for fetching paginated questions, filtering by source/category/difficulty/company,
stats reporting, bulk exporting, cold-start health checking, and triggering autonomous background pipeline scrapes.
"""

import os
import sys
import json
import threading
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Path, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Add pipeline directory to sys.path
pipeline_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline"))
if pipeline_dir not in sys.path:
    sys.path.insert(0, pipeline_dir)

app = FastAPI(
    title="Question Bank Generator API",
    description="Autonomous question bank API serving verified algorithmic and conceptual problems.",
    version="1.0.0"
)

# Enable CORS for frontend client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

_supabase_client = None

def get_supabase_client():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            return _supabase_client
        except Exception as e:
            print(f"[Backend] Warning: Failed to init Supabase client: {e}")
    return None

# Load local fallback questions if Supabase is offline
LOCAL_QUESTIONS_CACHE: List[Dict[str, Any]] = []

def load_local_fallback_questions():
    global LOCAL_QUESTIONS_CACHE
    local_paths = [
        os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "questions.json"),
        os.path.join(os.path.dirname(__file__), "..", "pipeline", "data", "questions.json"),
    ]

    for path in local_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    LOCAL_QUESTIONS_CACHE = json.load(f)
                    break
            except Exception as e:
                print(f"[Backend] Error loading fallback questions from {path}: {e}")

    return LOCAL_QUESTIONS_CACHE

# Background pipeline runner state
PIPELINE_RUNNING = False
LAST_PIPELINE_RUN_TIME = None
LAST_RUN_LOG = ""

def run_pipeline_task():
    global PIPELINE_RUNNING, LAST_PIPELINE_RUN_TIME, LAST_RUN_LOG
    if PIPELINE_RUNNING:
        print("[Backend Background Task] Pipeline is already running. Skipping trigger.")
        return

    PIPELINE_RUNNING = True
    print("[Backend Background Task] Starting 30-minute autonomous background scrape & verification pipeline...")
    try:
        from run_pipeline import main as run_master_pipeline
        run_master_pipeline()
        LAST_PIPELINE_RUN_TIME = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        LAST_RUN_LOG = "Pipeline completed successfully."
        load_local_fallback_questions()
    except Exception as e:
        print(f"[Backend Background Task] Error during background pipeline run: {e}")
        LAST_RUN_LOG = f"Error: {e}"
    finally:
        PIPELINE_RUNNING = False

# Periodic background thread (runs EVERY 30 MINUTES: 1800 seconds)
def start_periodic_scheduler():
    def loop():
        while True:
            # Sleep 30 minutes (1800 seconds) between automated scrapes
            time.sleep(1800)
            run_pipeline_task()

    t = threading.Thread(target=loop, daemon=True)
    t.start()

@app.on_event("startup")
def startup_event():
    load_local_fallback_questions()
    start_periodic_scheduler()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class ExportRequest(BaseModel):
    ids: List[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    """Cheap health check endpoint for frontend cold-start warming."""
    return {"status": "ok", "service": "question-bank-api", "pipeline_running": PIPELINE_RUNNING}


@app.post("/api/pipeline/run")
def trigger_pipeline_scrape(background_tasks: BackgroundTasks):
    """Triggers an autonomous scraping and verification pipeline run in the background."""
    global PIPELINE_RUNNING
    if PIPELINE_RUNNING:
        return {"status": "running", "message": "Pipeline is already running in the background."}

    background_tasks.add_task(run_pipeline_task)
    return {"status": "started", "message": "Pipeline scrape started in background."}


@app.get("/api/pipeline/status")
def get_pipeline_status():
    """Returns current background pipeline execution status."""
    return {
        "running": PIPELINE_RUNNING,
        "last_run_time": LAST_PIPELINE_RUN_TIME,
        "last_log": LAST_RUN_LOG
    }


@app.get("/api/questions")
def list_questions(
    source_site: Optional[str] = Query(None, description="Filter by source site"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    company: Optional[str] = Query(None, description="Filter by company"),
    verified: Optional[bool] = Query(None, description="Filter by verified boolean"),
    search: Optional[str] = Query(None, description="Search term for title or statement"),
    limit: int = Query(500, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Paginated endpoint for listing questions with server-side query filters.
    """
    client = get_supabase_client()
    if client:
        try:
            query = client.table("questions").select("*", count="exact")

            if source_site and source_site != "All":
                query = query.eq("source_site", source_site)
            if category and category != "All":
                query = query.eq("category", category)
            if difficulty and difficulty != "All":
                query = query.eq("difficulty", difficulty)
            if company and company != "All":
                query = query.contains("companies", [company])
            if verified is not None:
                query = query.eq("verified", verified)
            if search:
                query = query.ilike("title", f"%{search}%")

            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
            res = query.execute()

            items = res.data or []
            total = res.count or len(items)

            return {
                "items": items,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            print(f"[Backend] Error querying Supabase: {e}")

    # Fallback in-memory querying
    questions = load_local_fallback_questions()
    filtered = []

    for q in questions:
        q_source = q.get("source_site") or q.get("source")
        if source_site and source_site != "All" and q_source != source_site:
            continue
        if category and category != "All" and q.get("category") != category:
            continue
        if difficulty and difficulty != "All" and q.get("difficulty") != difficulty:
            continue
        if company and company != "All":
            comps = q.get("companies") or ([q.get("company")] if q.get("company") else [])
            if company not in comps:
                continue
        if verified is not None and bool(q.get("verified")) != verified:
            continue
        if search:
            s = search.lower()
            title = (q.get("title") or q.get("name") or "").lower()
            stmt = (q.get("problem_statement") or "").lower()
            if s not in title and s not in stmt:
                continue
        filtered.append(q)

    total = len(filtered)
    paged_items = filtered[offset : offset + limit]

    return {
        "items": paged_items,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/api/questions/{question_id:path}")
def get_question_by_id(question_id: str = Path(..., description="Target question ID")):
    """
    Returns full question record including solutions and test cases.
    """
    client = get_supabase_client()
    if client:
        try:
            res = client.table("questions").select("*").eq("id", question_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            print(f"[Backend] Error getting question by ID: {e}")

    # Fallback
    questions = load_local_fallback_questions()
    for q in questions:
        if q.get("id") == question_id or q.get("source_id") == question_id:
            return q

    raise HTTPException(status_code=404, detail="Question not found")


@app.get("/api/stats")
def get_stats():
    """
    Returns question bank statistics and last successful pipeline run timestamp.
    """
    client = get_supabase_client()
    if client:
        try:
            res_all = client.table("questions").select("source_site, category, difficulty, verified").execute()
            rows = res_all.data or []

            total = len(rows)
            verified_count = sum(1 for r in rows if r.get("verified"))
            verified_pct = round((verified_count / total * 100), 1) if total > 0 else 0.0

            by_source: Dict[str, int] = {}
            by_category: Dict[str, int] = {}
            by_difficulty: Dict[str, int] = {}

            for r in rows:
                s = r.get("source_site", "unknown")
                c = r.get("category", "Uncategorized")
                d = r.get("difficulty", "Medium")

                by_source[s] = by_source.get(s, 0) + 1
                by_category[c] = by_category.get(c, 0) + 1
                by_difficulty[d] = by_difficulty.get(d, 0) + 1

            last_run = None
            run_res = client.table("pipeline_runs").select("finished_at").in_("status", ["success", "partial"]).order("finished_at", desc=True).limit(1).execute()
            if run_res.data and len(run_res.data) > 0:
                last_run = run_res.data[0].get("finished_at")

            return {
                "total": total,
                "verified_count": verified_count,
                "verified_percentage": verified_pct,
                "by_source": by_source,
                "by_category": by_category,
                "by_difficulty": by_difficulty,
                "last_successful_run": last_run
            }
        except Exception as e:
            print(f"[Backend] Error fetching stats: {e}")

    # Fallback stats
    questions = load_local_fallback_questions()
    total = len(questions)
    verified_count = sum(1 for q in questions if q.get("verified"))
    verified_pct = round((verified_count / total * 100), 1) if total > 0 else 0.0

    by_source: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    by_difficulty: Dict[str, int] = {}

    for q in questions:
        s = q.get("source_site") or q.get("source") or "codeforces"
        c = q.get("category") or "Uncategorized"
        d = q.get("difficulty") or "Medium"
        by_source[s] = by_source.get(s, 0) + 1
        by_category[c] = by_category.get(c, 0) + 1
        by_difficulty[d] = by_difficulty.get(d, 0) + 1

    return {
        "total": total,
        "verified_count": verified_count,
        "verified_percentage": verified_pct,
        "by_source": by_source,
        "by_category": by_category,
        "by_difficulty": by_difficulty,
        "last_successful_run": LAST_PIPELINE_RUN_TIME
    }


@app.get("/api/sources")
def get_sources():
    """Returns distinct source sites with counts."""
    stats = get_stats()
    by_source = stats.get("by_source", {})
    return [{"source_site": s, "count": count} for s, count in sorted(by_source.items())]


@app.get("/api/companies")
def get_companies():
    """Returns distinct companies with counts."""
    client = get_supabase_client()
    if client:
        try:
            res = client.table("questions").select("companies").execute()
            rows = res.data or []
            counts: Dict[str, int] = {}
            for r in rows:
                comps = r.get("companies") or []
                for c in comps:
                    counts[c] = counts.get(c, 0) + 1
            return [{"company": c, "count": count} for c, count in sorted(counts.items())]
        except Exception as e:
            print(f"[Backend] Error fetching companies: {e}")

    # Fallback
    questions = load_local_fallback_questions()
    counts: Dict[str, int] = {}
    for q in questions:
        comps = q.get("companies") or ([q.get("company")] if q.get("company") else [])
        for c in comps:
            if c:
                counts[c] = counts.get(c, 0) + 1
    return [{"company": c, "count": count} for c, count in sorted(counts.items())]


@app.post("/api/export")
def export_questions(req: ExportRequest):
    """
    Returns array of question records matching requested IDs.
    """
    if not req.ids:
        return []

    client = get_supabase_client()
    if client:
        try:
            res = client.table("questions").select("*").in_("id", req.ids).execute()
            return res.data or []
        except Exception as e:
            print(f"[Backend] Error exporting questions: {e}")

    # Fallback
    questions = load_local_fallback_questions()
    target_ids = set(req.ids)
    return [q for q in questions if q.get("id") in target_ids or q.get("source_id") in target_ids]
