import json

with open('data/enriched_items.json', encoding='utf-8') as f:
    items = json.load(f)

found_any = False
for item in items:
    if item.get('item_type') == 'conceptual':
        continue
    tcs = item.get('test_cases', [])
    unique = {json.dumps(tc.get('input'), sort_keys=True) for tc in tcs}
    if len(unique) < len(tcs):
        print(f"{item.get('name')}: {len(unique)} unique out of {len(tcs)} test cases")
        found_any = True

if not found_any:
    print("No duplicate test cases found — all clean.")