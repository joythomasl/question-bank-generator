"""
classify.py — Stage 2: AI Classification & Tagging

Reads data/raw_items.json (from scrape.py) and, for each item, calls Groq to:
  - decide coding vs. conceptual
  - if coding: confirm/correct algorithm category (using the item's own
    Codeforces tags as a hint, not blind classification), assign difficulty,
    assign company (LeetCode-seed items already have this from scrape.py)
  - if conceptual: assign domain (Operating Systems / Machine Learning /
    DBMS / Networks / General CS) — this branch IS the bonus domain-detection
    feature, not a separate system

Output: data/tagged_items.json

STATUS: stub — classify_item() needs the actual Groq prompt/call filled in.
See docs/PROJECT_PLAN.md section 5 for the pipeline design this implements.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Groq is OpenAI-SDK compatible — same client, different base_url.
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "llama-3.3-70b-versatile"


def classify_item(item):
    """
    Takes one raw item (from raw_items.json) and returns it annotated with:
      - type: "coding" | "conceptual"
      - category (coding) or domain (conceptual)
      - difficulty
      - company

    TODO: build the Groq prompt using item['raw_text'], item.get('cf_tags'),
    item.get('difficulty_hint'), item.get('company_hint') as grounding,
    call client.chat.completions.create(...), parse the JSON response.
    """
    raise NotImplementedError("classify_item: fill in the Groq call")


def main():
    with open("data/raw_items.json") as f:
        raw_items = json.load(f)

    tagged = []
    for i, item in enumerate(raw_items):
        print(f"[{i + 1}/{len(raw_items)}] classifying: {item.get('name')}")
        tagged.append(classify_item(item))

    with open("data/tagged_items.json", "w") as f:
        json.dump(tagged, f, indent=2)

    print(f"Done. Wrote {len(tagged)} tagged items to data/tagged_items.json")


if __name__ == "__main__":
    main()
