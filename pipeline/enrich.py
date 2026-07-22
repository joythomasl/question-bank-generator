"""
enrich.py — Stage 3: Content Enrichment (concurrent)

Same generation logic/prompts/validation as before — the only change here
is running multiple items concurrently instead of one-at-a-time, since
NVIDIA's 40 RPM limit has room for several in-flight requests at once and
we were leaving that headroom unused waiting on each response sequentially.

Output is identical in content; this only changes wall-clock time.
"""

import json
import os
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

nvidia_client = None
if os.environ.get("NVIDIA_API_KEY"):
    nvidia_client = OpenAI(
        api_key=os.environ["NVIDIA_API_KEY"],
        base_url="https://integrate.api.nvidia.com/v1",
    )

groq_client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"
GROQ_MODEL = "llama-3.1-8b-instant"

MAX_RETRIES = 1
MAX_WORKERS = 10 # concurrent in-flight generations
TAGGED_ITEMS_PATH = "data/tagged_items.json"
ENRICHED_ITEMS_PATH = "data/enriched_items.json"

EDGE_CASE_TYPES = [
    "empty_or_minimal_input", "single_element", "all_duplicates",
    "sorted_ascending", "sorted_descending", "negative_numbers",
    "max_constraint_size", "boundary_value", "typical_case", "adversarial_case",
]

CODING_SYSTEM_PROMPT = f"""You generate original coding interview questions for a
curated question bank. You will be given a title, algorithm category, and
difficulty, and possibly brief source text for grounding only (do not copy wording).

You MUST follow this exact JSON shape — here is a real example for a different
problem, showing the required structure precisely:

{{"problem_statement": "Given an array of integers, return indices of the two numbers that add up to a target.",
"examples": [{{"input": "nums=[2,7,11,15], target=9", "output": "[0,1]", "explanation": "nums[0]+nums[1]=9"}}],
"constraints": ["2 <= nums.length <= 10^4"],
"test_cases": [{{"input": {{"nums": [2,7,11,15], "target": 9}}, "expected_output": [0,1], "edge_case_type": "typical_case"}}],
"python_solution": "def solve(nums, target):\\n    seen = {{}}\\n    for i, n in enumerate(nums):\\n        if target - n in seen:\\n            return [seen[target-n], i]\\n        seen[n] = i"}}

Now generate the same shape for the given title/category/difficulty:
1. problem_statement: original, self-contained.
2. examples: exactly 1 object with "input", "output", "explanation" — as STRINGS, matching the example above.
3. constraints: 2-3 short strings.
4. test_cases: exactly 10 objects. Each MUST have exactly the keys "input" (a JSON
   object of argument names to values), "expected_output", and "edge_case_type".
   Do NOT invent your own field names. Each test case's "input" values must be
   genuinely different from the others. Cover these types, one each:
   {EDGE_CASE_TYPES}
5. python_solution: a function named EXACTLY `solve` (not any other name),
   parameters matching test_cases' "input" keys exactly.

Respond with ONLY a JSON object in this exact shape, no markdown fences, no commentary.
"""

CONCEPTUAL_SYSTEM_PROMPT = """You generate original conceptual interview
questions for a curated question bank, given a topic and domain.

Generate concisely:
1. question: a clear conceptual interview question.
2. answer: 2-4 sentences.
3. key_points: 3 short key points.

Respond with ONLY a JSON object, no markdown fences, no commentary:
{"question": "...", "answer": "...", "key_points": [...]}
"""


class RateLimiter:
    """Sliding-window limiter — blocks callers instead of letting them fire
    and hit a 429/503. Set below NVIDIA's stated 40 RPM as safety margin."""
    def __init__(self, max_calls, period_seconds):
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = deque()
        self.lock = threading.Lock()

    def acquire(self):
        while True:
            with self.lock:
                now = time.time()
                while self.calls and now - self.calls[0] > self.period:
                    self.calls.popleft()
                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return
            time.sleep(0.1)


nvidia_limiter = RateLimiter(max_calls=32, period_seconds=60)  # 40 RPM stated, stay under it
save_lock = threading.Lock()
print_lock = threading.Lock()


def safe_print(msg):
    with print_lock:
        print(msg, flush=True)


def item_key(item):
    source = item.get("source")
    if source == "codeforces":
        return f"cf:{item.get('contestId')}:{item.get('index')}"
    elif source == "wikipedia":
        return f"wiki:{item.get('name')}"
    elif source == "leetcode_company_csv":
        return f"lc:{item.get('company_hint')}:{item.get('name')}"
    return f"unknown:{item.get('name')}"


def build_coding_prompt(item):
    lines = [
        f"Title: {item.get('name')}",
        f"Category: {item.get('category')}",
        f"Difficulty: {item.get('difficulty')}",
    ]
    if item.get("raw_text"):
        lines.append(f"Source (grounding only):\n{item['raw_text'][:350]}")
    return "\n\n".join(lines)


def build_conceptual_prompt(item):
    lines = [f"Title: {item.get('name')}", f"Domain: {item.get('domain')}"]
    if item.get("raw_text"):
        lines.append(f"Source (grounding only):\n{item['raw_text'][:350]}")
    return "\n\n".join(lines)


def call_model(client, model, system_prompt, user_prompt, is_nvidia):
    if is_nvidia:
        nvidia_limiter.acquire()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=2500,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    return json.loads(content)


DAILY_WALL_MARKERS = ["tokens per day", "TPD", "rate_limit_exceeded"]
PERMANENT_MARKERS = ["model_not_found", "404", "402", "payment_required", "NOT_FOUND"]
TRANSIENT_MARKERS = ["503", "ResourceExhausted", "timeout", "connection"]


def enrich_with_fallback(system_prompt, user_prompt):
    providers = []
    if nvidia_client:
        providers.append((nvidia_client, NVIDIA_MODEL, "nvidia", True))
    providers.append((groq_client, GROQ_MODEL, "groq", False))

    for client, model, label, is_nvidia in providers:
        for attempt in range(MAX_RETRIES + 1):
            try:
                return call_model(client, model, system_prompt, user_prompt, is_nvidia), None
            except (json.JSONDecodeError, KeyError):
                if attempt == MAX_RETRIES:
                    break
                time.sleep(1)
            except Exception as e:
                error_str = str(e)
                if any(m in error_str for m in DAILY_WALL_MARKERS):
                    return None, "daily_wall"
                if any(m in error_str for m in PERMANENT_MARKERS):
                    break
                if any(m in error_str for m in TRANSIENT_MARKERS) and attempt < MAX_RETRIES:
                    time.sleep(3)
                    continue
                if attempt == MAX_RETRIES:
                    break
                time.sleep(2)
    return None, "all_providers_failed"


def enrich_coding_item(item):
    result, failure = enrich_with_fallback(CODING_SYSTEM_PROMPT, build_coding_prompt(item))
    if result is None:
        return None, failure

    python_solution = (result.get("python_solution") or "").strip()
    test_cases = result.get("test_cases") or []

    if not python_solution or "def solve(" not in python_solution:
        return None, "wrong_function_name_or_empty"
    if len(test_cases) < 10:
        return None, "incomplete_generation"
    if not all(isinstance(tc, dict) and "input" in tc and "expected_output" in tc for tc in test_cases):
        return None, "wrong_test_case_schema"

    unique_inputs = {json.dumps(tc.get("input"), sort_keys=True) for tc in test_cases}
    if len(unique_inputs) < 7:
        return None, "duplicate_test_cases"

    return {
        **item,
        "problem_statement": result.get("problem_statement"),
        "examples": result.get("examples"),
        "constraints": result.get("constraints"),
        "test_cases": test_cases,
        "solutions": {"python": python_solution, "java": None},
        "verified": False,
    }, None


def enrich_conceptual_item(item):
    result, failure = enrich_with_fallback(CONCEPTUAL_SYSTEM_PROMPT, build_conceptual_prompt(item))
    if result is None:
        return None, failure
    return {
        **item,
        "question": result.get("question"),
        "answer": result.get("answer"),
        "key_points": result.get("key_points"),
        "verified": True,
    }, None


def process_item(item):
    if item.get("item_type") == "conceptual":
        return item, enrich_conceptual_item(item)
    return item, enrich_coding_item(item)


def load_existing_enriched():
    try:
        with open(ENRICHED_ITEMS_PATH, encoding="utf-8") as f:
            existing = json.load(f)
    except FileNotFoundError:
        return {}
    return {item_key(item): item for item in existing}


def save_enriched(enriched_by_key):
    with save_lock:
        with open(ENRICHED_ITEMS_PATH, "w", encoding="utf-8") as f:
            json.dump(list(enriched_by_key.values()), f, indent=2, ensure_ascii=False)


def main():
    with open(TAGGED_ITEMS_PATH, encoding="utf-8") as f:
        tagged_items = json.load(f)

    enriched_by_key = load_existing_enriched()
    if enriched_by_key:
        print(f"Resuming — {len(enriched_by_key)} items already enriched, skipping those.")

    to_process = [item for item in tagged_items if item_key(item) not in enriched_by_key]
    total = len(to_process)
    print(f"{total} items left to enrich. Running {MAX_WORKERS} concurrent, "
          f"NVIDIA: {'enabled' if nvidia_client else 'disabled'}\n")

    stop_flag = threading.Event()
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for item in to_process:
            if stop_flag.is_set():
                break
            futures[executor.submit(process_item, item)] = item

        for future in as_completed(futures):
            completed += 1
            item, (result, failure) = future.result()
            label = item.get("name")

            if result is not None:
                enriched_by_key[item_key(item)] = result
                save_enriched(enriched_by_key)
                safe_print(f"[{completed}/{total}] OK: {label}")
            elif failure == "daily_wall":
                safe_print(f"[{completed}/{total}] >>> Hit Groq's daily wall — NVIDIA should keep going.")
            else:
                safe_print(f"[{completed}/{total}] DROPPED ({failure}): {label}")

    dropped = len(tagged_items) - len(enriched_by_key)
    print(f"\nProgress: {len(enriched_by_key)} enriched in {ENRICHED_ITEMS_PATH} ({dropped} not yet done)")


if __name__ == "__main__":
    main()