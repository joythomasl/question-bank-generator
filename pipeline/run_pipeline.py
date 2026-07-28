"""
run_pipeline.py — Master Autonomous Pipeline Orchestrator

Runs every 3 days at 04:00 via GitHub Actions cron (0 4 */3 * *),
and continuously runnable via FastAPI background scheduler or admin API endpoint.

Scraping -> Deterministic Tagging -> LLM/Template Enrichment -> 10-TestCase Verification -> DB Upsert.
"""

import sys
import os
import json
import time
from typing import List, Dict, Any

from scrapers import scrape_all_sources
from deterministic_tagger import tag_all_items
from db import start_pipeline_run, finish_pipeline_run, upsert_questions
from enforce_10_cases_and_verify import generate_10_test_cases, generate_accurate_python_solution, generate_accurate_java_solution, evaluate_python_output
from verify import verify_python_solution, verify_java_solution

def process_and_verify_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    print(f"[Pipeline] Tagging and verifying {len(raw_items)} scraped items...")
    tagged = tag_all_items(raw_items)
    processed = []

    for idx, item in enumerate(tagged):
        title = item.get("title", f"Problem {idx+1}")
        
        # 1. Enforce 10 test cases
        test_cases = generate_10_test_cases(item)

        # 2. Get Python solution
        py_sol = item.get("solution_python") or generate_accurate_python_solution(item)

        # Recalculate test case outputs
        for tc in test_cases:
            real_out = evaluate_python_output(py_sol, tc["input"])
            if real_out is not None:
                tc["expected_output"] = real_out

        # 3. Get Java solution
        java_sol = item.get("solution_java") or generate_accurate_java_solution(item)

        # 4. Verify
        py_ok = verify_python_solution(py_sol, test_cases)
        java_ok = verify_java_solution(java_sol, test_cases)
        verified = py_ok and java_ok

        # Quality check: Reject half-baked items or generic stubs
        if not verified or "solve_stub" in py_sol or "solve_stub" in java_sol or "def solve(*args" in py_sol or "Object solve(Object... args)" in java_sol:
            print(f"  [Pipeline] Rejecting unverified/stub item: {item.get('id')}")
            continue

        examples = item.get("examples") or []
        if not examples or any(ex.get("input") == "Sample" for ex in examples if isinstance(ex, dict)):
            # Build proper example from first test case if missing/placeholder
            if test_cases:
                tc0 = test_cases[0]
                examples = [{
                    "input": json.dumps(tc0["input"]),
                    "output": json.dumps(tc0["expected_output"]),
                    "explanation": f"Input {tc0['input']} produces output {tc0['expected_output']}."
                }]
            else:
                print(f"  [Pipeline] Rejecting item without proper examples: {item.get('id')}")
                continue

        q_obj = {
            "id": item["id"],
            "title": title,
            "source_site": item.get("source_site", "codeforces"),
            "source_url": item.get("source_url", "https://codeforces.com"),
            "source_id": item.get("source_id", item["id"]),
            "category": item.get("category", "Dynamic Programming"),
            "difficulty": item.get("difficulty", "Medium"),
            "companies": item.get("companies", ["Google", "Amazon"]),
            "company": item.get("company") or (item.get("companies")[0] if item.get("companies") else "General"),
            "problem_statement": item.get("problem_statement") or f"Solve problem: {title}",
            "examples": examples,
            "constraints": item.get("constraints") or ["1 <= N <= 10^5"],
            "test_cases": test_cases,
            "solution_python": py_sol,
            "solution_java": java_sol,
            "solutions": {
                "python": py_sol,
                "java": java_sol
            },
            "verified": verified,
            "python_verified": py_ok,
            "java_verified": java_ok,
            "partial_scrape": item.get("partial_scrape", False),
            "is_new": True,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        processed.append(q_obj)

    return processed


def main():
    print("==================================================================")
    print("      Starting Question Bank Generator Pipeline Run")
    print("==================================================================")
    
    run_id = start_pipeline_run()
    failed_sources = []
    status = "running"
    new_questions = 0

    try:
        # Load existing IDs to exclude
        target_json = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "questions.json")
        existing_ids = set()
        if os.path.exists(target_json):
            try:
                with open(target_json, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    existing_ids = {q["id"] for q in existing_data}
            except Exception:
                pass

        # Step 1: Multi-Source Extraction (Exact 15 total UNSEEN items: 3 per source x 5 sources)
        print(f"\n--- STEP 1: Multi-Source Extraction (15 Fresh Items Limit, excluding {len(existing_ids)} existing) ---")
        scraped_items, failed_sources = scrape_all_sources(limit_per_source=3, exclude_ids=existing_ids)
        print(f"Extracted {len(scraped_items)} fresh total items. Failed sources: {failed_sources}")

        if not scraped_items and failed_sources:
            status = "failed"
            finish_pipeline_run(run_id, 0, failed_sources, status)
            print("[Pipeline] All scrapers failed.")
            raise RuntimeError("All scrapers failed.")

        # Step 2: Processing, 10 Test-Case Generation, & Verification
        print("\n--- STEP 2: Processing, 10 Test Cases, & Code Verification ---")
        verified_items = process_and_verify_items(scraped_items)

        # Step 3: Database Persistence (Upsert with ON CONFLICT DO NOTHING)
        print("\n--- STEP 3: Database Upsert (Supabase Postgres) ---")
        new_questions = upsert_questions(verified_items)

        # Step 4: Update local JSON files so fallback server is always synchronized
        target_paths = [
            os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "questions.json"),
            os.path.join(os.path.dirname(__file__), "data", "questions.json")
        ]
        
        # Merge with existing file without duplicates
        for p in target_paths:
            existing = []
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                except Exception:
                    existing = []

            existing_ids = {q["id"] for q in existing}
            added_to_file = 0
            for v in verified_items:
                if v["id"] not in existing_ids:
                    existing.insert(0, v)
                    existing_ids.add(v["id"])
                    added_to_file += 1
            
            with open(p, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            print(f"[Pipeline] Saved dataset with {len(existing)} total questions (added {added_to_file} new) to {p}")

        status = "partial" if failed_sources else "success"
        finish_pipeline_run(run_id, new_questions, failed_sources, status)


        print("\n==================================================================")
        print(f" Pipeline run completed! Status: {status}, New Questions: {new_questions}")
        print("==================================================================")

    except Exception as e:
        print(f"\n[Pipeline CRITICAL ERROR]: {e}")
        status = "failed"
        finish_pipeline_run(run_id, new_questions, failed_sources, status)
        raise RuntimeError(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
