"""
add_java.py — adds Java solutions to an already-exported questions.json,
without touching anything else. Standalone, safe to run after the fact.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

nvidia_client = OpenAI(api_key=os.environ["NVIDIA_API_KEY"], base_url="https://integrate.api.nvidia.com/v1")
MODEL = "meta/llama-3.3-70b-instruct"
QUESTIONS_PATH = "data/questions.json"

JAVA_PROMPT = """Convert this Python solution (function `solve`) into an
equivalent Java solution, as a single class named `Solution` with a public
method named `solve`. Respond with ONLY a JSON object:
{{"java_solution": "..."}}

Python:
{code}
"""


def generate_and_check_java(item):
    py_code = (item.get("solutions") or {}).get("python")
    if not py_code or item.get("type") != "coding":
        return item
    try:
        r = nvidia_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": JAVA_PROMPT.format(code=py_code)}],
            temperature=0.3, max_tokens=1000,
            response_format={"type": "json_object"},
        )
        content = r.choices[0].message.content.strip().strip("`")
        if content.startswith("json"):
            content = content[4:]
        java_code = json.loads(content).get("java_solution")

        tmp_dir = tempfile.mkdtemp()
        java_path = Path(tmp_dir) / "Solution.java"
        java_path.write_text(java_code, encoding="utf-8")
        compiled = subprocess.run(["javac", str(java_path)], capture_output=True, timeout=5, cwd=tmp_dir).returncode == 0

        item["solutions"]["java"] = java_code if compiled else None
        item["java_verified"] = compiled
    except Exception as e:
        print(f"  {item.get('title')}: {e}")
    return item


with open(QUESTIONS_PATH, encoding="utf-8") as f:
    questions = json.load(f)

with ThreadPoolExecutor(max_workers=6) as ex:
    futures = [ex.submit(generate_and_check_java, q) for q in questions]
    updated = [f.result() for f in as_completed(futures)]

with open(QUESTIONS_PATH, "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

added = sum(1 for q in questions if (q.get("solutions") or {}).get("java"))
print(f"Done. {added}/{len(questions)} items now have compiled Java.")