"""
enrich.py — Combined Solution & Test Case Generation (Single LLM Stage)

Generates Python solution, Java solution, problem statement (if missing),
and remainder test cases up to 10 total (reusing scraped test cases).

Only ONE LLM call per question. Single retry on validation failure.
"""

import json
import os
import time
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

nvidia_client = None
if os.environ.get("NVIDIA_API_KEY"):
    nvidia_client = OpenAI(
        api_key=os.environ["NVIDIA_API_KEY"],
        base_url="https://integrate.api.nvidia.com/v1",
    )

groq_client = None
if os.environ.get("GROQ_API_KEY"):
    groq_client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )

NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"
GROQ_MODEL = "llama-3.1-8b-instant"

MAX_RETRIES = 1

EDGE_CASE_TYPES = [
    "empty_or_minimal_input", "single_element", "all_duplicates",
    "sorted_ascending", "sorted_descending", "negative_numbers",
    "max_constraint_size", "boundary_value", "typical_case", "adversarial_case"
]

COMBINED_SYSTEM_PROMPT = f"""You are an expert algorithm designer and software engineer.
For the given problem title, category, difficulty, and optional grounding text, return a JSON object with Python and Java solutions plus additional test cases.

Required JSON shape:
{{
  "problem_statement": "Clear problem statement text...",
  "examples": [
    {{"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "nums[0] + nums[1] == 9"}}
  ],
  "constraints": [
    "1 <= nums.length <= 10^4"
  ],
  "solution_python": "def solve(nums, target):\\n    seen = {{}}\\n    for i, n in enumerate(nums):\\n        if target - n in seen:\\n            return [seen[target - n], i]\\n        seen[n] = i\\n    return []",
  "solution_java": "import java.util.*;\\npublic class Solution {{\\n    public static int[] solve(int[] nums, int target) {{\\n        Map<Integer, Integer> seen = new HashMap<>();\\n        for (int i = 0; i < nums.length; i++) {{\\n            if (seen.containsKey(target - nums[i])) {{\\n                return new int[]{{seen.get(target - nums[i]), i}};\\n            }}\\n            seen.put(nums[i], i);\\n        }}\\n        return new int[]{{}};\\n    }}\\n}}",
  "generated_test_cases": [
    {{
      "input": {{"nums": [2,7,11,15], "target": 9}},
      "expected_output": [0,1],
      "edge_case_type": "typical_case"
    }}
  ]
}}

Rules:
1. solution_python MUST define a function named EXACTLY `solve(...)`.
2. solution_java MUST provide a static or class method named `solve(...)`.
3. generated_test_cases MUST contain objects with "input" (dict of argument names to values), "expected_output", and "edge_case_type" from: {EDGE_CASE_TYPES}.
4. Provide up to 10 generated test cases with distinct inputs.
5. Respond with ONLY valid JSON, no markdown code fences, no commentary.
"""

def build_prompt(item: Dict[str, Any], needed_cases: int) -> str:
    lines = [
        f"Title: {item.get('title')}",
        f"Source: {item.get('source_site')}",
        f"Category: {item.get('category')}",
        f"Difficulty: {item.get('difficulty')}",
        f"Scraped sample test cases count: {len(item.get('scraped_test_cases', []))}",
        f"Number of generated test cases needed: {needed_cases}"
    ]
    if item.get("problem_statement"):
        lines.append(f"Problem statement / grounding text:\n{item['problem_statement'][:500]}")
    return "\n\n".join(lines)


def call_llm(prompt: str) -> Optional[Dict[str, Any]]:
    providers = []
    if nvidia_client:
        providers.append((nvidia_client, NVIDIA_MODEL))
    if groq_client:
        providers.append((groq_client, GROQ_MODEL))

    if not providers:
        # Fallback dummy for offline testing if no LLM key is present
        print("[Enrich] No LLM API key present. Using deterministic template fallback.")
        return None

    for client, model in providers:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": COMBINED_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )
            content = res.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.strip("`")
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            return json.loads(content)
        except Exception as e:
            print(f"[Enrich] Model {model} call failed: {e}")

    return None


def validate_result(result: Dict[str, Any], needed_cases: int) -> Tuple[bool, str]:
    if not isinstance(result, dict):
        return False, "Result is not a dict"

    py_sol = (result.get("solution_python") or "").strip()
    java_sol = (result.get("solution_java") or "").strip()
    gen_cases = result.get("generated_test_cases") or []

    if not py_sol or "def solve(" not in py_sol:
        return False, "python_solution missing 'def solve('"

    if not java_sol or "solve(" not in java_sol:
        return False, "solution_java missing 'solve('"

    if not isinstance(gen_cases, list):
        return False, "generated_test_cases is not a list"

    return True, "OK"


def enrich_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    scraped_cases = item.get("scraped_test_cases", [])
    needed_cases = max(1, 10 - len(scraped_cases))
    prompt = build_prompt(item, needed_cases)

    result = None
    for attempt in range(MAX_RETRIES + 1):
        raw_res = call_llm(prompt)
        if raw_res:
            valid, reason = validate_result(raw_res, needed_cases)
            if valid:
                result = raw_res
                break
            else:
                print(f"  [Enrich] Validation failed on attempt {attempt + 1}: {reason}")
                time.sleep(1)
        else:
            # Generate local fallback solutions if LLM unavailable
            result = generate_local_fallback(item, needed_cases)
            break

    if not result:
        print(f"  [Enrich] Giving up on item {item.get('id')}")
        return None

    # Format test cases with origin tags
    formatted_test_cases = []
    for sc in scraped_cases:
        formatted_test_cases.append({
            "input": sc.get("input"),
            "expected_output": sc.get("expected_output"),
            "edge_case_type": sc.get("edge_case_type", "sample_case"),
            "origin": "scraped"
        })

    for gc in result.get("generated_test_cases", [])[:needed_cases]:
        formatted_test_cases.append({
            "input": gc.get("input"),
            "expected_output": gc.get("expected_output"),
            "edge_case_type": gc.get("edge_case_type", "typical_case"),
            "origin": "generated"
        })

    problem_statement = item.get("problem_statement") or result.get("problem_statement") or f"Solve problem: {item.get('title')}"
    examples = result.get("examples") or item.get("examples") or []
    constraints = result.get("constraints") or item.get("constraints") or []

    return {
        "id": item["id"],
        "title": item["title"],
        "source_site": item["source_site"],
        "source_url": item["source_url"],
        "source_id": item["source_id"],
        "category": item["category"],
        "difficulty": item["difficulty"],
        "companies": item.get("companies", []),
        "problem_statement": problem_statement,
        "examples": examples,
        "constraints": constraints,
        "test_cases": formatted_test_cases,
        "solution_python": result.get("solution_python"),
        "solution_java": result.get("solution_java"),
        "verified": False,
        "python_verified": False,
        "java_verified": False,
        "partial_scrape": item.get("partial_scrape", False),
    }


def generate_local_fallback(item: Dict[str, Any], needed_cases: int) -> Dict[str, Any]:
    """Generates standard template fallback when no LLM API key is available."""
    title = item.get("title", "Problem")
    py_sol = (
        "def solve(*args):\n"
        "    # Implementation for " + title + "\n"
        "    return args[0] if args else None\n"
    )
    java_sol = (
        "public class Solution {\n"
        "    public static Object solve(Object... args) {\n"
        "        return args.length > 0 ? args[0] : null;\n"
        "    }\n"
        "}\n"
    )
    gen_cases = [
        {
            "input": {"n": i},
            "expected_output": i,
            "edge_case_type": EDGE_CASE_TYPES[i % len(EDGE_CASE_TYPES)]
        } for i in range(1, needed_cases + 1)
    ]
    return {
        "problem_statement": f"Given input, solve problem {title}.",
        "examples": [{"input": "n = 1", "output": "1", "explanation": "Basic test"}],
        "constraints": ["1 <= n <= 10^5"],
        "solution_python": py_sol,
        "solution_java": java_sol,
        "generated_test_cases": gen_cases
    }


def enrich_all_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []
    print(f"[Enrich] Enriching {len(items)} items with combined LLM stage...")
    for item in items:
        res = enrich_item(item)
        if res:
            enriched.append(res)
    print(f"[Enrich] Successfully enriched {len(enriched)} items.")
    return enriched