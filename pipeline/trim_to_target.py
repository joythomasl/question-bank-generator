"""
trim_to_target.py — cap the enrichment pool at TARGET_TOTAL, without losing
any items already successfully enriched.
"""
import json

TAGGED_ITEMS_PATH = "data/tagged_items.json"
ENRICHED_ITEMS_PATH = "data/enriched_items.json"
TARGET_TOTAL = 380

def item_key(item):
    source = item.get("source")
    if source == "codeforces":
        return f"cf:{item.get('contestId')}:{item.get('index')}"
    elif source == "wikipedia":
        return f"wiki:{item.get('name')}"
    elif source == "leetcode_company_csv":
        return f"lc:{item.get('company_hint')}:{item.get('name')}"
    return f"unknown:{item.get('name')}"

with open(TAGGED_ITEMS_PATH, encoding="utf-8") as f:
    tagged_items = json.load(f)

with open(ENRICHED_ITEMS_PATH, encoding="utf-8") as f:
    enriched_items = json.load(f)

enriched_keys = {item_key(i) for i in enriched_items}
already_done = [i for i in tagged_items if item_key(i) in enriched_keys]
remaining = [i for i in tagged_items if item_key(i) not in enriched_keys]

keep_count = max(0, TARGET_TOTAL - len(already_done))
trimmed_remaining = remaining[:keep_count]
final_items = already_done + trimmed_remaining

with open(TAGGED_ITEMS_PATH, "w", encoding="utf-8") as f:
    json.dump(final_items, f, indent=2, ensure_ascii=False)

print(f"Already enriched: {len(already_done)}")
print(f"Remaining pool: {len(remaining)} -> trimmed to {len(trimmed_remaining)}")
print(f"New tagged_items.json total: {len(final_items)}")
print(f"Expect final verified count somewhat BELOW {TARGET_TOTAL} after enrich/verify attrition.")
