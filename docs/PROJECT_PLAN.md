# Automated Programming Question Generator — Final Project Plan

## 1. Goal

A pre-generated, machine-verified bank of 500+ interview questions (algorithmic
+ bonus conceptual), viewable in a fast static portal, with checkbox-based
selective JSON export. Zero cost to build or run. No live AI calls in the
deployed app — every question is generated and verified *before* the demo,
not during it.

---

## 2. Full Feature List

| # | Feature | How it's satisfied |
|---|---|---|
| 1 | Detailed problem statement, examples w/ explanation, constraints, 10 edge-case test cases | `enrich.py` (Groq generation) + fixed question schema |
| 2 | Company tag or "General" | Two-track sourcing: LeetCode CSVs (real company data) + Codeforces (honestly "General") |
| 3 | Difficulty tag (Easy/Medium/Hard) | Codeforces numeric rating → bucketed; LeetCode CSV's own difficulty column |
| 4 | Python + Java solutions, both passing all test cases | `verify.py` — local subprocess sandbox, execute-and-retry loop, non-negotiable gate before storage |
| 5 | Checkbox-select → JSON download | Fully client-side in the static frontend, no backend call |
| 6 | Bonus: non-programming detection (OS/ML) | `classify.py` routing step + Wikipedia-sourced conceptual raw text as realistic scrape input |
| 7 | ~~AI code analysis vs. optimal~~ | **Cut** — out of scope per final decision; project is a question generator, not a live grader |
| 8 | 500+ pre-generated, pre-verified questions | Offline batch pipeline, Codeforces volume + LeetCode seeds |
| 9 | Strictly free to build and operate | Groq free tier (generation) + static hosting (Vercel/Netlify free tier) + local execution sandbox (no Judge0 dependency) |

---

## 3. Architecture — Two Phases, Only One Touches the Internet at Demo Time

```
PHASE 1 — OFFLINE GENERATION (run once, before the demo, on your machine)
  scrape.py    → raw_items.json
  classify.py  → tagged_items.json
  enrich.py    → enriched_items.json
  verify.py    → questions.db (SQLite, only verified rows survive)
  export.py    → questions.json (final static bundle)

PHASE 2 — STATIC PORTAL (what judges actually see and click through)
  React + Tailwind + shadcn/ui, built as a static site
  Loads questions.json directly — no backend, no API, no server
  All filtering/search/checkbox-select/download happens in-browser
  Hosted free on Vercel or Netlify
```

**Why this matters:** nothing in the deployed app can fail due to venue wifi,
rate limits, or a flaky LLM call during your live demo. Every question a
judge sees has already been generated *and machine-verified* beforehand.

---

## 4. Data Sources (Stage 1 — Scraping)

| Source | What's pulled | Used for |
|---|---|---|
| **Codeforces official API + page scrape** | Real problem statements (BeautifulSoup-cleaned HTML) + community tags (`dp`, `greedy`, `two pointers`, `divide and conquer`) + numeric rating | Primary volume driver — thousands of candidates available, genuinely public, no paywall |
| **Wikipedia** (Virtual Memory, Gradient Descent, Deadlocks, Overfitting, etc.) | Intro paragraphs as raw conceptual text | Feeds the domain-detection bonus — realistic messy input for the classifier to correctly route as "not a coding problem" |
| **Public LeetCode company-wise GitHub CSVs** (e.g. `liquidslr/leetcode-company-wise-problems`) | Title + company + difficulty **only** — no problem text | Real company tags + Backtracking seeds (CF doesn't tag Backtracking well) |

**Explicitly not scraped:** LeetCode's actual paywalled problem pages — bot-protected,
largely Premium-gated, and a bad scrape target regardless of project scale.
The company/title metadata from the CSVs above is public and freely re-shared;
the actual problem *content* for those titles is generated fresh by the LLM,
never pulled from LeetCode itself.

**Rejected idea:** fuzzy-matching CF problem titles against LeetCode titles to
backfill company tags. Too little real overlap to be useful, and loose
matching risks asserting false company attributions — a worse look than an
honest "General" given accuracy is scored.

---

## 5. Pipeline Stages

### Stage 1 — `scrape.py` ✅ written
Pulls raw candidates from Codeforces (real scrape), Wikipedia (bonus), and
LeetCode CSVs (company/difficulty seeds only). Outputs `raw_items.json`.

### Stage 2 — `classify.py` (next)
One Groq call per item. Branches on coding vs. conceptual:
- **Coding:** confirm/correct category (using CF's own tags as a hint, not
  blind guessing), difficulty, company
- **Conceptual:** domain (OS / ML / DBMS / Networks / General CS)

This single branch *is* the "bonus" domain-detection feature — not a
separate system.

### Stage 3 — `enrich.py`
Takes classified raw text as grounding and generates the standardized,
original content: problem statement, 2 worked examples with step-by-step
explanation, constraints, and exactly 10 test cases (empty/minimal input,
single element, all-duplicates, sorted ascending/descending, negatives,
max-constraint size, boundary value, typical case, adversarial case) plus
a Python reference solution.

### Stage 4 — `verify.py`
Executes the generated Python solution against the 10 generated test cases
in a local `subprocess` sandbox (no Judge0 dependency, no rate limit, free).
Mismatches trigger a feedback-and-retry loop (max 2 retries) before a
question is discarded. Once Python passes, Java is generated and validated
the same way via `javac`/`java` subprocess calls. Only `verified: true`
rows are ever written to `questions.db`.

### Stage 5 — `export.py`
Dumps the verified table into one static `questions.json` bundle for the
frontend to import directly.

---

## 6. Question Schema

```json
{
  "id": "dp-014",
  "title": "Longest Increasing Subsequence",
  "category": "Dynamic Programming",
  "difficulty": "Medium",
  "company": ["Amazon", "General"],
  "problem_statement": "...",
  "examples": [
    {"input": "...", "output": "...", "explanation": "..."}
  ],
  "constraints": ["1 <= n <= 10^4", "..."],
  "test_cases": [
    {"input": {"...": "..."}, "expected_output": "...", "edge_case_type": "empty_input"}
  ],
  "solutions": {
    "python": "def solve(...): ...",
    "java": "class Solution { ... }"
  },
  "verified": true,
  "source": "codeforces | leetcode_company_csv",
  "tags": ["array", "binary-search"]
}
```

Non-programming (bonus) items use a parallel schema: `domain` instead of
`category`, `answer` + `key_points` instead of test cases/solutions.

---

## 7. Tech Stack

| Layer | Choice | Cost |
|---|---|---|
| Generation LLM | Groq free tier (Llama 3.3 70B / Qwen / GPT-OSS-120B) | Free — 30 RPM, ~1,000–14,400 req/day depending on model |
| Solution verification | Local `subprocess` sandbox (Python + Java) | Free — no Judge0 dependency, no rate limit |
| Working DB during generation | SQLite | Free |
| Final data bundle | Static `questions.json` | Free |
| Frontend | Vite + React + Tailwind + shadcn/ui + Framer Motion | Free, open source |
| Charts (stats dashboard, optional) | Recharts | Free |
| In-browser code demo (optional polish) | Pyodide | Free, runs client-side |
| Hosting | Vercel / Netlify free tier (static site, no backend) | Free |

---

## 8. Why This Is Genuinely Free

- Groq's free tier requires no credit card and covers this project's volume
  comfortably: ~600–900 total generation calls (500+ questions × ~1.5 calls
  average with retries) fits well inside daily/per-minute caps.
- No Judge0, no paid execution API — verification runs locally.
- No backend server at all in the deployed app — static hosting has no
  compute cost and nothing to keep "warm."
- Seed data (GitHub CSVs, Codeforces, Wikipedia) are all public, no API key
  or subscription required.

---

## 9. Volume Math

- Codeforces alone realistically yields 1,000+ raw scraped candidates across
  the 4 CF-taggable categories.
- LeetCode CSVs (capped per company, deduped across companies) contribute
  roughly 300–350 unique company-tagged seed titles.
- After the verify-and-retry gate (expect ~75–85% survival — normal
  attrition, not a bug), realistic final count: **700–1,200+ verified
  questions**, comfortably clearing the 500 minimum with real headroom.
- Of these, **~230–300 will carry a genuine company tag**; the rest are
  honestly "General" (mostly the Codeforces track, which has no real
  company signal to begin with).

---

## 10. Frontend Feature Checklist

**Required:**
- Card/grid view with category, difficulty, company filter chips + search
- Detail view: statement, examples, constraints, all 10 test cases,
  Python/Java toggle with syntax highlighting
- Checkbox per card + sticky "Download Selected (N)" bar
- "Select all" / "select all in category" convenience buttons

**Polish (free, optional, high visual payoff):**
- "AI-Verified ✓" badge on every question (communicates the execution
  validation pipeline without needing to explain it to judges)
- Stats dashboard: category distribution, difficulty split, company coverage
- Dark mode, skeleton loaders, subtle hover/expand animations
- Optional Pyodide-powered "run this Python solution live" button per
  question — pure demo polish, not required functionality

---

## 11. Known, Honest Limitations (worth stating upfront rather than getting caught on)

- Company tags are largely absent for Codeforces-sourced questions —
  structural, not a bug, since CF problems were never asked in a corporate
  interview.
- LeetCode-track questions have AI-generated (not scraped) statement text,
  because the real LeetCode pages are paywalled/bot-protected — the company
  tag is real, sourced from public metadata; the content is generated and
  verified, not lifted from LeetCode itself.
- Live AI code-analysis (comparing a user's submission to the optimal
  solution) was explicitly scoped out — this project generates and verifies
  questions, it does not grade live user submissions.
- No pagination/backend planned — fine at hundreds of rows in one static
  JSON file; would need revisiting only if this grew to a much larger
  public-scale dataset.

---

## 12. Scoring Alignment

| Judging criterion | What demonstrates it |
|---|---|
| Volume | 700–1,200+ verified questions, shown via the stats dashboard |
| Accuracy — tagging | CF's own community tags used as a hint (not blind classification), reducing misclassification risk |
| Accuracy — edge cases | 10 structured test case types generated per question, not arbitrary |
| Accuracy — code correctness | Non-negotiable execute-and-verify gate; only compiled/passing code is ever stored |
| Bonus — domain detection | Wikipedia-sourced conceptual items prove the classifier actually routes coding vs. conceptual correctly, not just in theory |

---

## 13. Build Order / Status

- [x] `scrape.py` — Codeforces + Wikipedia + LeetCode CSV loader
- [ ] `classify.py` — category/domain + difficulty + company routing
- [ ] `enrich.py` — statement + examples + constraints + test cases + solutions
- [ ] `verify.py` — subprocess sandbox execution + retry loop
- [ ] `export.py` — SQLite → static `questions.json`
- [ ] Frontend — static React portal, checkbox/download, filters
