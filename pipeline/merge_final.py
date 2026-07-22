"""
merge_final.py — combine the coding-question export and the conceptual-
question export into one final questions.json.
"""

import json

with open("data/questions.json", encoding="utf-8") as f:
    coding_questions = json.load(f)

with open("data/conceptual_direct.json", encoding="utf-8") as f:
    conceptual_questions = json.load(f)

final = coding_questions + conceptual_questions

with open("data/questions.json", "w", encoding="utf-8") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)

print(f"Final: {len(coding_questions)} coding + {len(conceptual_questions)} conceptual = {len(final)} total")