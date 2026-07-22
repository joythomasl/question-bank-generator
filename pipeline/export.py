"""
export.py — Stage 5: Export to static bundle

Reads only verified rows from data/questions.db and writes them into
data/questions.json — the single static file the frontend loads directly.
No backend server reads this database at runtime; this script is the only
bridge between the offline pipeline and the deployed static site.
"""

import json
import sqlite3

DB_PATH = "data/questions.db"
OUTPUT_PATH = "data/questions.json"


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM questions WHERE verified = 1").fetchall()

    questions = []
    for row in rows:
        questions.append(
            {
                "id": row["id"],
                "title": row["title"],
                "category": row["category"],
                "difficulty": row["difficulty"],
                "company": json.loads(row["company"]) if row["company"] else "General",
                "problem_statement": row["problem_statement"],
                "examples": json.loads(row["examples_json"]) if row["examples_json"] else [],
                "constraints": json.loads(row["constraints_json"]) if row["constraints_json"] else [],
                "test_cases": json.loads(row["test_cases_json"]) if row["test_cases_json"] else [],
                "solutions": {
                    "python": row["solution_python"],
                    "java": row["solution_java"],
                },
                "verified": bool(row["verified"]),
                "source": row["source"],
                "tags": json.loads(row["tags_json"]) if row["tags_json"] else [],
            }
        )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"Done. Exported {len(questions)} verified questions to {OUTPUT_PATH}")
    print("Copy this file into frontend/src/data/ (replacing mockQuestions.js's")
    print("export, or fetch it at runtime) before building/deploying the frontend.")


if __name__ == "__main__":
    main()
