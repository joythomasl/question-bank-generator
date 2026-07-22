"""
verify.py — Stage 4: Code Validation (Execution Engine)

Runs every generated Python solution against its 10 test cases in an
isolated subprocess (no Judge0, no rate limit — local and free).

Speed/time-crunch mode: no LLM fix-retry, no Java generation (Groq's daily
budget is exhausted anyway, so those calls were just wasted wait time).
Items that fail verification are KEPT in the output with verified=False
rather than dropped — the frontend's "Verified" badge already only shows
for verified=True, so nothing is misrepresented, but nothing that was
successfully enriched gets silently thrown away either.

Conceptual items pass through untouched (already verified in enrich.py).

Checkpointed — safe to interrupt/resume. Reads with retry-on-parse-error
in case enrich.py is still mid-write on the same file (should be rare/never
now that enrich.py's save is atomic, but cheap insurance either way).

Output: data/verified_items.json
"""

import json
import os
import subprocess
import tempfile
import time

ENRICHED_ITEMS_PATH = "data/enriched_items.json"
VERIFIED_ITEMS_PATH = "data/verified_items.json"
TIMEOUT_SECONDS = 2  # down from 5 — fail fast on broken/looping solutions

PYTHON_RUNNER_TEMPLATE = '''
import json, sys
{solution_code}

test_input = json.loads(sys.argv[1])
try:
    try:
        result = solve(**test_input)
    except TypeError:
        result = solve(*test_input.values())
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"__error__": str(e)}}))
'''


def run_python_test(solution_code, test_input):
    runner = PYTHON_RUNNER_TEMPLATE.format(solution_code=solution_code)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(runner)
        tmp_path = f.name
    try:
        result = subprocess.run(
            ['python', tmp_path, json.dumps(test_input)],
            capture_output=True, text=True, encoding='utf-8', timeout=TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            return None, result.stderr.strip()[:300]
        output = json.loads(result.stdout.strip())
        if isinstance(output, dict) and "__error__" in output:
            return None, output["__error__"]
        return output, None
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except Exception as e:
        return None, str(e)
    finally:
        os.unlink(tmp_path)


def outputs_match(actual, expected):
    if actual == expected:
        return True
    # Type-lenient comparisons — catch correct answers marked wrong due to
    # incidental type differences (list vs tuple, int vs float, bool vs 1/0),
    # not real logic errors.
    try:
        if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
            return list(actual) == list(expected)
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            return abs(actual - expected) < 1e-6
        if isinstance(actual, bool) or isinstance(expected, bool):
            return bool(actual) == bool(expected)
    except TypeError:
        pass
    return False


def verify_python_solution(solution_code, test_cases):
    failures = []
    for tc in test_cases:
        actual, error = run_python_test(solution_code, tc.get("input", {}))
        if error is not None:
            failures.append({**tc, "actual": None, "error": error})
        elif not outputs_match(actual, tc.get("expected_output")):
            failures.append({**tc, "actual": actual, "error": None})
    return len(failures) == 0, failures


def item_key(item):
    source = item.get("source")
    if source == "codeforces":
        return f"cf:{item.get('contestId')}:{item.get('index')}"
    elif source == "wikipedia":
        return f"wiki:{item.get('name')}"
    elif source == "leetcode_company_csv":
        return f"lc:{item.get('company_hint')}:{item.get('name')}"
    return f"unknown:{item.get('name')}"


def load_enriched_items():
    for attempt in range(3):
        try:
            with open(ENRICHED_ITEMS_PATH, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            if attempt == 2:
                raise
            time.sleep(1)


def load_existing_verified():
    try:
        with open(VERIFIED_ITEMS_PATH, encoding="utf-8") as f:
            existing = json.load(f)
    except FileNotFoundError:
        return {}
    return {item_key(item): item for item in existing}


def save_verified(verified_by_key):
    tmp_path = VERIFIED_ITEMS_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(list(verified_by_key.values()), f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, VERIFIED_ITEMS_PATH)


def verify_coding_item(item):
    solution_code = item.get("solutions", {}).get("python")
    test_cases = item.get("test_cases") or []
    if not solution_code or not test_cases:
        return None  # structurally incomplete — nothing to verify at all

    passed, failures = verify_python_solution(solution_code, test_cases)

    return {
        **item,
        "solutions": {"python": solution_code, "java": None},
        "verified": passed,
        "python_verified": passed,
        "java_verified": False,
    }


def main():
    enriched_items = load_enriched_items()

    verified_by_key = load_existing_verified()
    if verified_by_key:
        print(f"Resuming — {len(verified_by_key)} items already processed, skipping those.")

    to_process = [item for item in enriched_items if item_key(item) not in verified_by_key]
    print(f"{len(to_process)} items left to verify.\n")

    passed_count = 0
    failed_count = 0
    skipped_count = 0

    for i, item in enumerate(to_process):
        label = item.get("name") or item.get("title")
        print(f"[{i + 1}/{len(to_process)}] verifying: {label}")

        if item.get("item_type") == "conceptual":
            result = item
        else:
            result = verify_coding_item(item)

        if result is not None:
            verified_by_key[item_key(item)] = result
            save_verified(verified_by_key)
            if result.get("verified"):
                passed_count += 1
                print("  PASSED")
            else:
                failed_count += 1
                print("  FAILED (kept, unverified)")
        else:
            skipped_count += 1
            print("  SKIPPED — no solution/test cases at all")

    print(f"\nDone. {len(verified_by_key)} total items in {VERIFIED_ITEMS_PATH}")
    print(f"  {passed_count} passed verification")
    print(f"  {failed_count} failed but kept (verified=False)")
    print(f"  {skipped_count} skipped (nothing to verify)")


if __name__ == "__main__":
    main()