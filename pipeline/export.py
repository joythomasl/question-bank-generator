"""
export.py — Stage 5: Export to static bundle

Reads data/verified_items.json (written directly by verify.py — there is no
intermediate sqlite database in this pipeline) and writes data/questions.json,
the single static file the frontend loads at runtime. No backend server reads
this at runtime; this script is the only bridge between the offline pipeline
and the deployed static site.

Coding items and conceptual (bonus domain-detection) items use different
field shapes downstream, but share a common envelope (id, title, item_type,
difficulty, difficultyColor, company, verified, source, tags) so the frontend
can list/filter/search them together.
"""

import json

VERIFIED_ITEMS_PATH = "data/verified_items.json"
OUTPUT_PATH = "data/questions.json"

CATEGORY_PREFIX = {
    "Dynamic Programming": "dp",
    "Backtracking": "bt",
    "Greedy": "gr",
    "Divide and Conquer": "dc",
    "Two Pointers": "tp",
}
DOMAIN_PREFIX = {
    "Operating Systems": "os",
    "Machine Learning": "ml",
    "DBMS": "db",
    "Networks": "nw",
    "General CS": "cs",
}
DIFFICULTY_COLOR = {"Easy": "verified", "Medium": "warn", "Hard": "danger"}


def make_id(prefix, counters):
    counters[prefix] = counters.get(prefix, 0) + 1
    return f"{prefix}-{counters[prefix]:03d}"


def export_coding(item, counters):
    category = item.get("category") or "Dynamic Programming"
    prefix = CATEGORY_PREFIX.get(category, "misc")
    difficulty = item.get("difficulty") or "Medium"
    return {
        "id": make_id(prefix, counters),
        "title": item.get("name") or "Untitled",
        "item_type": "coding",
        "category": category,
        "difficulty": difficulty,
        "difficultyColor": DIFFICULTY_COLOR.get(difficulty, "warn"),
        "company": item.get("company") or "General",
        "verified": bool(item.get("verified")),
        "problem_statement": item.get("problem_statement"),
        "examples": item.get("examples") or [],
        "constraints": item.get("constraints") or [],
        "test_cases": item.get("test_cases") or [],
        "solutions": {
            "python": (item.get("solutions") or {}).get("python"),
            "java": (item.get("solutions") or {}).get("java"),
        },
        "source": item.get("source"),
        "tags": item.get("cf_tags") or [],
    }


def export_conceptual(item, counters):
    domain = item.get("domain") or "General CS"
    prefix = DOMAIN_PREFIX.get(domain, "cs")
    difficulty = item.get("difficulty") or "Medium"
    return {
        "id": make_id(prefix, counters),
        "title": item.get("name") or "Untitled",
        "item_type": "conceptual",
        "domain": domain,
        "difficulty": difficulty,
        "difficultyColor": DIFFICULTY_COLOR.get(difficulty, "warn"),
        "company": item.get("company") or "General",
        "verified": bool(item.get("verified")),
        "question": item.get("question"),
        "answer": item.get("answer"),
        "key_points": item.get("key_points") or [],
        "source": item.get("source"),
        "tags": [],
    }


def main():
    with open(VERIFIED_ITEMS_PATH, encoding="utf-8") as f:
        verified_items = json.load(f)

    counters = {}
    questions = []
    for item in verified_items:
        if not item.get("verified"):
            continue
        if item.get("item_type") == "conceptual":
            questions.append(export_conceptual(item, counters))
        else:
            questions.append(export_coding(item, counters))

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    coding_count = sum(1 for q in questions if q["item_type"] == "coding")
    conceptual_count = sum(1 for q in questions if q["item_type"] == "conceptual")
    print(f"Done. Exported {len(questions)} verified questions to {OUTPUT_PATH}")
    print(f"  {coding_count} coding, {conceptual_count} conceptual")
    print("Copy this file into frontend/public/questions.json before building/deploying.")


if __name__ == "__main__":
    main()
