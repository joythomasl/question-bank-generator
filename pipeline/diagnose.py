import json
from collections import Counter

with open('data/raw_items.json', encoding='utf-8') as f:
    raw = json.load(f)

def item_key(item):
    source = item.get("source")
    if source == "codeforces":
        return f"cf:{item.get('contestId')}:{item.get('index')}"
    elif source == "wikipedia":
        return f"wiki:{item.get('name')}"
    elif source == "leetcode_company_csv":
        return f"lc:{item.get('company_hint')}:{item.get('name')}"
    return f"unknown:{item.get('name')}"

keys = [item_key(i) for i in raw]
counter = Counter(keys)
dupes = {k: v for k, v in counter.items() if v > 1}

print(f"Total raw items: {len(raw)}")
print(f"Unique keys: {len(counter)}")
print(f"Duplicate keys: {len(dupes)} (accounting for {sum(dupes.values()) - len(dupes)} extra entries)")
for k, v in list(dupes.items())[:10]:
    print(f"  {k} appears {v} times")