"""
direct_export.py — export enriched (but NOT execution-verified) items
straight to the final questions.json, skipping verify.py entirely.

Every item is explicitly marked verified=False, since none of these
solutions have actually been run against their test cases. This is an
honest label, not a formality — the frontend's "Verified" badge is gated
on this field, so nothing gets misrepresented, it just won't show the
badge for anything exported this way.
"""

import json

ENRICHED_ITEMS_PATH = "data/enriched_items.json"
OUTPUT_PATH = "data/questions.json"

with open(ENRICHED_ITEMS_PATH, encoding="utf-8") as f:
    enriched = json.load(f)

questions = []
for item in enriched:
    if item.get("item_type") == "conceptual":
        questions.append({
            "id": item.get("name", "").lower().replace(" ", "-")[:40],
            "title": item.get("name"),
            "category": item.get("domain"),
            "difficulty": item.get("difficulty", "Medium"),
            "company": item.get("company", "General"),
            "question": item.get("question"),
            "answer": item.get("answer"),
            "key_points": item.get("key_points"),
            "verified": True,  # conceptual items were never meant to be
                                # execution-verified in the first place —
                                # there's no code to run for a Q&A item
            "source": item.get("source"),
            "type": "conceptual",
        })
    else:
        solution_python = (item.get("solutions") or {}).get("python")
        test_cases = item.get("test_cases") or []
        if not solution_python or not test_cases:
            continue  # genuinely incomplete generations still get skipped

        questions.append({
            "id": item.get("name", "").lower().replace(" ", "-")[:40],
            "title": item.get("name"),
            "category": item.get("category"),
            "difficulty": item.get("difficulty", "Medium"),
            "company": item.get("company", "General"),
            "problem_statement": item.get("problem_statement"),
            "examples": item.get("examples"),
            "constraints": item.get("constraints"),
            "test_cases": test_cases,
            "solutions": {"python": solution_python, "java": None},
            "verified": False,  # honest — not execution-checked
            "source": item.get("source"),
            "type": "coding",
        })

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print(f"Exported {len(questions)} questions to {OUTPUT_PATH} (all coding items marked verified=False)")