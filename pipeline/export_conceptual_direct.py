"""
export_conceptual_direct.py — export conceptual (Wikipedia-sourced) items
directly from the recovered raw backup, no LLM enrichment needed.
"""

import json

BACKUP_PATH = "C:/Users/Joy Thomas/Downloads/question-bank-generator/raw_items_backup.json"
OUTPUT_PATH = "data/conceptual_direct.json"

with open(BACKUP_PATH, encoding="utf-8") as f:
    backup_items = json.load(f)

wiki_items = [x for x in backup_items if x.get("source") == "wikipedia"]

questions = []
for item in wiki_items:
    raw_text = item.get("raw_text") or ""
    if not raw_text.strip():
        continue
    questions.append({
        "id": item.get("name", "").lower().replace(" ", "-")[:40],
        "title": item.get("name"),
        "category": item.get("domain_hint"),
        "difficulty": "Medium",
        "company": "General",
        "question": f"Explain {item.get('name')} and its significance.",
        "answer": raw_text[:800],
        "key_points": [],
        "verified": True,
        "source": "wikipedia",
        "type": "conceptual",
    })

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print(f"Exported {len(questions)} conceptual items to {OUTPUT_PATH}")