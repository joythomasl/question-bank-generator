"""
verify.py — Stage 4: Code Validation (Execution Engine)

Reads data/enriched_items.json. For each coding item, runs the generated
Python solution against the 10 generated test cases in a local subprocess
sandbox (no Judge0 dependency — free, no rate limit). On mismatch, feeds the
failure back to Groq for a fix and retries (max 2 retries). Once Python
passes 10/10, generates and validates a Java solution the same way.

Only items that pass both languages get verified=True and are written to
data/questions.db (SQLite). Everything else is discarded — this gate is
non-negotiable, since it's the backbone of the project's accuracy story.

Output: data/questions.db

STATUS: stub — run_python_sandboxed(), run_java_sandboxed(), and the
retry loop need to be filled in.
"""

import json
import sqlite3
import subprocess

DB_PATH = "data/questions.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            title TEXT,
            category TEXT,
            difficulty TEXT,
            company TEXT,
            problem_statement TEXT,
            examples_json TEXT,
            constraints_json TEXT,
            test_cases_json TEXT,
            solution_python TEXT,
            solution_java TEXT,
            verified BOOLEAN DEFAULT 0,
            source TEXT,
            tags_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cat ON questions(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_diff ON questions(difficulty)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_company ON questions(company)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_verified ON questions(verified)")
    conn.commit()
    return conn


def run_python_sandboxed(solution_code, test_case_input):
    """
    TODO: write solution_code + a small harness to a temp file, run it via
    `subprocess.run([...], timeout=5, capture_output=True)`, parse stdout,
    return the actual output (or an error).
    """
    raise NotImplementedError("run_python_sandboxed: implement subprocess execution")


def run_java_sandboxed(solution_code, test_case_input):
    """
    TODO: write solution_code to Solution.java, `javac` it, then `java` it
    with the test case input, same subprocess pattern as Python.
    """
    raise NotImplementedError("run_java_sandboxed: implement javac/java execution")


def verify_item(item):
    """
    TODO: run item's Python solution against all 10 test cases via
    run_python_sandboxed. On any mismatch, retry (max 2) by feeding the
    failure back to Groq for a fix. Once Python passes, do the same for Java.
    Return (item, verified: bool).
    """
    raise NotImplementedError("verify_item: implement the verify-and-retry loop")


def main():
    with open("data/enriched_items.json") as f:
        enriched_items = json.load(f)

    conn = init_db()
    verified_count = 0

    for i, item in enumerate(enriched_items):
        print(f"[{i + 1}/{len(enriched_items)}] verifying: {item.get('title')}")
        if item.get("type") == "conceptual":
            # Conceptual items skip execution verification entirely.
            verified_item, is_verified = item, True
        else:
            verified_item, is_verified = verify_item(item)

        if is_verified:
            verified_count += 1
            conn.execute(
                """
                INSERT OR REPLACE INTO questions
                (id, title, category, difficulty, company, problem_statement,
                 examples_json, constraints_json, test_cases_json,
                 solution_python, solution_java, verified, source, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    verified_item.get("id"),
                    verified_item.get("title"),
                    verified_item.get("category"),
                    verified_item.get("difficulty"),
                    json.dumps(verified_item.get("company")),
                    verified_item.get("problem_statement"),
                    json.dumps(verified_item.get("examples")),
                    json.dumps(verified_item.get("constraints")),
                    json.dumps(verified_item.get("test_cases")),
                    verified_item.get("solutions", {}).get("python"),
                    verified_item.get("solutions", {}).get("java"),
                    True,
                    verified_item.get("source"),
                    json.dumps(verified_item.get("tags")),
                ),
            )
            conn.commit()

    print(f"Done. {verified_count}/{len(enriched_items)} items verified and stored.")


if __name__ == "__main__":
    main()
