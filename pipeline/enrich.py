"""
enrich.py — Stage 3: Content Enrichment

Reads data/tagged_items.json and, for each coding item, calls Groq to generate
the standardized, original content: problem statement, 2 worked examples with
step-by-step explanation, constraints, exactly 10 test cases (covering the
standard edge-case types — see docs/PROJECT_PLAN.md), and a Python reference
solution.

For conceptual (bonus) items, generates: answer + key_points instead.

Output: data/enriched_items.json

STATUS: stub — enrich_coding_item() and enrich_conceptual_item() need the
actual Groq prompt/call filled in.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "llama-3.3-70b-versatile"

EDGE_CASE_TYPES = [
    "empty_or_minimal_input",
    "single_element",
    "all_duplicates",
    "sorted_ascending",
    "sorted_descending",
    "negative_numbers",
    "max_constraint_size",
    "boundary_value",
    "typical_case",
    "adversarial_case",
]


def enrich_coding_item(item):
    """
    TODO: prompt Groq for problem_statement, examples, constraints,
    10 test_cases (using EDGE_CASE_TYPES as the required coverage list),
    and a Python solution. Return item merged with this content.
    """
    raise NotImplementedError("enrich_coding_item: fill in the Groq call")


def enrich_conceptual_item(item):
    """
    TODO: prompt Groq for answer + key_points for a conceptual/bonus item.
    """
    raise NotImplementedError("enrich_conceptual_item: fill in the Groq call")


def main():
    with open("data/tagged_items.json") as f:
        tagged_items = json.load(f)

    enriched = []
    for i, item in enumerate(tagged_items):
        print(f"[{i + 1}/{len(tagged_items)}] enriching: {item.get('name')}")
        if item.get("type") == "conceptual":
            enriched.append(enrich_conceptual_item(item))
        else:
            enriched.append(enrich_coding_item(item))

    with open("data/enriched_items.json", "w") as f:
        json.dump(enriched, f, indent=2)

    print(f"Done. Wrote {len(enriched)} enriched items to data/enriched_items.json")


if __name__ == "__main__":
    main()
