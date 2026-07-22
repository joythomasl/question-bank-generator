"""
trim_remaining.py — cut the classification pool down to a token-budget-
realistic size, without losing the 132 items already classified.
"""
import json

RAW_ITEMS_PATH = "data/raw_items.json"
TAGGED_ITEMS_PATH = "data/tagged_items.json"
TARGET_TOTAL = 750

with open(RAW_ITEMS_PATH, encoding="utf-8") as f:
    raw_items = json.load(f)
with open(TAGGED_ITEMS_PATH, encoding="utf-8") as f:
    tagged_items = json.load(f)

def item_key(item):
    source = item.get("source")
    if source == "codeforces":
        return f"cf:{item.get('contestId')}:{item.get('index')}"
    elif source == "wikipedia":
        return f"wiki:{item.get('name')}"
    elif source == "leetcode_company_csv":
        return f"lc:{item.get('company_hint')}:{item.get('name')}"
    return f"unknown:{item.get('name')}"

tagged_keys = {item_key(i) for i in tagged_items}
already_done = [i for i in raw_items if item_key(i) in tagged_keys]
remaining = [i for i in raw_items if item_key(i) not in tagged_keys]

keep_count = max(0, TARGET_TOTAL - len(already_done))
trimmed_remaining = remaining[:keep_count]
final_items = already_done + trimmed_remaining

with open(RAW_ITEMS_PATH, "w", encoding="utf-8") as f:
    json.dump(final_items, f, indent=2, ensure_ascii=False)

print(f"Already classified: {len(already_done)}")
print(f"Remaining pool: {len(remaining)} -> trimmed to {len(trimmed_remaining)}")
print(f"New raw_items.json total: {len(final_items)}")