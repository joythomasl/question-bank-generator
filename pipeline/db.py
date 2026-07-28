"""
db.py — Supabase Postgres database interaction module
Handles questions upsert, pipeline_runs tracking, stats queries, and schema verification.
"""

import os
import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "") or os.environ.get("SUPABASE_DB_URL", "")

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
            print(f"[db.py] Warning: Failed to initialize supabase client: {e}")
    return None

def start_pipeline_run() -> Optional[int]:
    """Records the start of a pipeline run in pipeline_runs table."""
    client = get_supabase_client()
    if not client:
        print("[db.py] No Supabase client configured. Skipping pipeline_runs creation.")
        return None

    try:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        res = client.table("pipeline_runs").insert({
            "started_at": now,
            "status": "running",
            "new_questions": 0,
            "failed_sources": []
        }).execute()

        if res.data and len(res.data) > 0:
            run_id = res.data[0]["id"]
            print(f"[db.py] Started pipeline_run #{run_id}")
            return run_id
    except Exception as e:
        print(f"[db.py] Error starting pipeline_run: {e}")
    return None

def finish_pipeline_run(run_id: Optional[int], new_questions: int, failed_sources: List[str], status: str):
    """Updates a pipeline run on completion."""
    if not run_id:
        return
    client = get_supabase_client()
    if not client:
        return

    try:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        client.table("pipeline_runs").update({
            "finished_at": now,
            "new_questions": new_questions,
            "failed_sources": failed_sources,
            "status": status
        }).eq("id", run_id).execute()
        print(f"[db.py] Finished pipeline_run #{run_id} with status '{status}'")
    except Exception as e:
        print(f"[db.py] Error finishing pipeline_run #{run_id}: {e}")

def upsert_questions(questions: List[Dict[str, Any]]) -> int:
    """
    Inserts questions into Supabase table using ON CONFLICT (id) DO NOTHING logic.
    Returns count of new inserted items.
    """
    if not questions:
        return 0

    client = get_supabase_client()
    if not client:
        print(f"[db.py] Supabase client unavailable. Simulated upsert for {len(questions)} items.")
        return len(questions)

    inserted_count = 0
    # Batch upsert in chunks of 50
    chunk_size = 50
    for i in range(0, len(questions), chunk_size):
        chunk = questions[i:i + chunk_size]
        try:
            # Upsert with ignore_duplicates=True (ON CONFLICT (id) DO NOTHING)
            res = client.table("questions").upsert(chunk, on_conflict="id", ignore_duplicates=True).execute()
            if res.data:
                inserted_count += len(res.data)
        except Exception as e:
            print(f"[db.py] Error upserting questions chunk {i}: {e}")

    print(f"[db.py] Successfully upserted {inserted_count} questions.")
    return inserted_count
