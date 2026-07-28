"""
verify_all_61_solutions.py — End-to-end verification harness for Python & Java solutions
across all 61 questions in questions.json.
"""

import os
import sys
import json
import tempfile
import subprocess
import shutil

# Ensure path to pipeline
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline")))

from verify import verify_python_solution, verify_java_solution

def test_everything():
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "questions.json"))
    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"==================================================================")
    print(f" RUNNING RIGOROUS VERIFICATION ON {len(questions)} QUESTIONS")
    print(f"==================================================================")

    py_passed = 0
    java_passed = 0

    for idx, q in enumerate(questions):
        title = q.get("title", f"Question {idx+1}")
        q_id = q.get("id")
        py_sol = q.get("solution_python") or (q.get("solutions") or {}).get("python")
        java_sol = q.get("solution_java") or (q.get("solutions") or {}).get("java")
        test_cases = q.get("test_cases", [])

        # Python test
        py_ok = verify_python_solution(py_sol, test_cases)
        if py_ok:
            py_passed += 1

        # Java test
        java_ok = verify_java_solution(java_sol, test_cases)
        if java_ok:
            java_passed += 1

        py_str = "PASS" if py_ok else "FAIL"
        java_str = "PASS" if java_ok else "FAIL"

        print(f"[{idx+1}/{len(questions)}] {q_id} - '{title}'")
        print(f"    Python: {py_str} | Java: {java_str} | Test cases: {len(test_cases)}")

    print(f"\n==================================================================")
    print(f" VERIFICATION SUMMARY:")
    print(f" Python Passed: {py_passed}/{len(questions)} ({round(py_passed/len(questions)*100, 1)}%)")
    print(f" Java Passed:   {java_passed}/{len(questions)} ({round(java_passed/len(questions)*100, 1)}%)")
    print(f"==================================================================")

    return py_passed == len(questions) and java_passed == len(questions)

if __name__ == "__main__":
    success = test_everything()
    if not success:
        sys.exit(1)
