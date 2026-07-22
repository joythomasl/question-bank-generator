"""
dedupe_seeds.py — one-time cleanup pass on raw_items.json
"""

import json
from collections import defaultdict

INPUT_PATH = "raw_items.json"
OUTPUT_PATH = "raw_items.json"
PER_COMPANY_CAP = 40

with open(INPUT_PATH, encoding="utf-8") as f:
    items = json.load(f)

company_items = [i for i in items if i.get("source") == "leetcode_company_csv"]
other_items = [i for i in items if i.get("source") != "leetcode_company_csv"]

print(f"Before cleanup: {len(company_items)} company-seed items across "
      f"{len(set(i['company_hint'] for i in company_items))} companies")

by_company = defaultdict(dict)
for item in company_items:
    key = item["name"].strip().lower()
    company = item["company_hint"]
    if key not in by_company[company]:
        by_company[company][key] = item

deduped_capped = []
for company, titles in by_company.items():
    capped = list(titles.values())[:PER_COMPANY_CAP]
    print(f"  {company}: {len(titles)} unique -> keeping {len(capped)}")
    deduped_capped.extend(capped)

final_items = other_items + deduped_capped

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(final_items, f, indent=2, ensure_ascii=False)

print(f"\nDone. {len(items)} -> {len(final_items)} total items "
      f"({len(other_items)} CF/Wikipedia + {len(deduped_capped)} company-seed)")