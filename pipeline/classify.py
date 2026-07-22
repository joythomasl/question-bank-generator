"""
classify.py — Stage 2: AI Classification & Tagging

Reads data/raw_items.json and, for each item, calls Groq to decide:
  1. item_type: "coding" or "conceptual" — the model decides this itself from
     the raw text, it does NOT just trust which scraper produced the item.
  2. category (if coding) or domain (if conceptual)
  3. difficulty
  4. company

Checkpointed: writes data/tagged_items.json after every item, and skips
anything already classified on a rerun — safe to interrupt and resume.

Output: data/tagged_items.json
"""

import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "llama-3.1-8b-instant"
MAX_RETRIES = 2
SECONDS_BETWEEN_CALLS = 2.5
RAW_ITEMS_PATH = "data/raw_items.json"
TAGGED_ITEMS_PATH = "data/tagged_items.json"

CATEGORIES = [
    "Dynamic Programming",
    "Backtracking",
    "Greedy",
    "Divide and Conquer",
    "Two Pointers",
]
DOMAINS = ["Operating Systems", "Machine Learning", "DBMS", "Networks", "General CS"]

SYSTEM_PROMPT = f"""You are a strict classifier for a coding interview question bank.
Given raw text (which may be a competitive-programming problem statement, an
encyclopedia excerpt on a CS concept, or just a problem title), decide:

1. item_type: "coding" if this is an algorithmic problem to solve with code,
   or "conceptual" if this is a theory/definition question with no code to write.

2. If coding: category — exactly one of {CATEGORIES}.
3. If conceptual: domain — exactly one of {DOMAINS}.

If a hint is provided in the input, prefer it unless the text clearly
contradicts it — do not override a correct hint just to seem independent.

4. difficulty — exactly one of "Easy", "Medium", "Hard".
5. company — a specific company name if one is clearly implied by a hint,
   otherwise "General".

Respond with ONLY a JSON object, no markdown fences, no commentary:
{{"item_type": "...", "category": "..." or null, "domain": "..." or null,
  "difficulty": "...", "company": "..."}}
"""


def item_key(item):
    """Stable identity for resume support — same idea as scrape.py's resume logic."""
    source = item.get("source")
    if source == "codeforces":
        return f"cf:{item.get('contestId')}:{item.get('index')}"
    elif source == "wikipedia":
        return f"wiki:{item.get('name')}"
    elif source == "leetcode_company_csv":
        return f"lc:{item.get('company_hint')}:{item.get('name')}"
    return f"unknown:{item.get('name')}"


def build_user_prompt(item):
    lines = [f"Title: {item.get('name', 'Unknown')}"]

    if item.get("raw_text"):
        lines.append(f"Raw text:\n{item['raw_text'][:800]}")
    if item.get("cf_tags"):
        lines.append(f"Source tags (hint): {', '.join(item['cf_tags'])}")
    if item.get("category_hint"):
        lines.append(f"Category hint: {item['category_hint']}")
    if item.get("domain_hint"):
        lines.append(f"Domain hint: {item['domain_hint']}")
    if item.get("difficulty_hint"):
        lines.append(f"Difficulty hint: {item['difficulty_hint']}")
    if item.get("company_hint"):
        lines.append(f"Company hint: {item['company_hint']}")

    return "\n\n".join(lines)


def classify_item(item):
    user_prompt = build_user_prompt(item)
    result = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.strip("`")
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            result = json.loads(content)
            break
        except (json.JSONDecodeError, KeyError) as e:
            if attempt == MAX_RETRIES:
                print(f"  FAILED to classify '{item.get('name')}' after retries: {e}")
                return None
            time.sleep(1)
        except Exception as e:
            if attempt == MAX_RETRIES:
                print(f"  FAILED (API error) '{item.get('name')}': {e}")
                return None
            print(f"  retrying after error: {e}")
            time.sleep(5)

    if result is None:
        return None

    return {
        **item,
        "item_type": result.get("item_type", item.get("type", "coding")),
        "category": result.get("category"),
        "domain": result.get("domain"),
        "difficulty": result.get("difficulty", item.get("difficulty_hint", "Medium")),
        "company": result.get("company", item.get("company_hint", "General")),
    }


def load_existing_tagged():
    try:
        with open(TAGGED_ITEMS_PATH, encoding="utf-8") as f:
            existing = json.load(f)
    except FileNotFoundError:
        return {}
    return {item_key(item): item for item in existing}


def save_tagged(tagged_by_key):
    with open(TAGGED_ITEMS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(tagged_by_key.values()), f, indent=2, ensure_ascii=False)


def main():
    with open(RAW_ITEMS_PATH, encoding="utf-8") as f:
        raw_items = json.load(f)

    tagged_by_key = load_existing_tagged()
    already_done = len(tagged_by_key)
    if already_done:
        print(f"Resuming — {already_done} items already classified, skipping those.")

    to_process = [item for item in raw_items if item_key(item) not in tagged_by_key]
    print(f"{len(to_process)} items left to classify.")

    for i, item in enumerate(to_process):
        print(f"[{i + 1}/{len(to_process)}] classifying: {item.get('name')}")
        result = classify_item(item)
        if result is not None:
            tagged_by_key[item_key(item)] = result
            save_tagged(tagged_by_key)  # checkpoint after every item
        time.sleep(SECONDS_BETWEEN_CALLS)

    dropped = len(raw_items) - len(tagged_by_key)
    print(f"\nDone. {len(tagged_by_key)} tagged items in {TAGGED_ITEMS_PATH} ({dropped} dropped)")


if __name__ == "__main__":
    main()