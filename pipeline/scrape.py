"""
scrape.py — Stage 1: Data Extraction

Pulls raw problem data from:
  1. Codeforces (official API for metadata + tags/rating, BeautifulSoup for
     the actual problem statement HTML) — this is the primary, real scrape.
  2. Wikipedia articles on OS/ML concepts — raw text used to demonstrate the
     "conceptual question" bonus-detection path in classify.py.
  3. A public LeetCode company-wise CSV (from GitHub) — used ONLY for
     (title, company, difficulty) seed metadata, never for problem text.
     (See https://github.com/liquidslr/leetcode-company-wise-problems or
     https://github.com/snehasishroy/leetcode-companywise-interview-questions
     for raw CSV URLs to paste into COMPANY_CSV_URLS below.)

Output: raw_items.json — a list of raw, uncleaned candidate items to be fed
into classify.py and enrich.py next.

Run:
    pip install requests beautifulsoup4
    python scrape.py
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# Config — tune these for more/less volume
# ---------------------------------------------------------------------------

CF_API = "https://codeforces.com/api/problemset.problems"
CF_PROBLEM_URL = "https://codeforces.com/problemset/problem/{contestId}/{index}"

# Codeforces tag -> our category mapping.
# NOTE: Codeforces doesn't meaningfully tag "backtracking" as its own thing —
# that category is sourced separately from the LeetCode company CSV seeds below.
TAG_MAP = {
    "dp": "Dynamic Programming",
    "greedy": "Greedy",
    "divide and conquer": "Divide and Conquer",
    "two pointers": "Two Pointers",
}

PROBLEMS_PER_CATEGORY = 120   # raise this for more raw candidates -> more volume
REQUEST_DELAY_SEC = 0.4       # politeness delay between individual page fetches
MAX_WORKERS = 4                # modest concurrency, keeps CF happy

WIKIPEDIA_CONCEPTS = {
    "Operating Systems": [
        "Virtual_memory", "Deadlock_(computer_science)", "Process_scheduling",
        "Paging", "Thread_(computing)", "Context_switch",
        "Cache_replacement_policies", "Semaphore_(programming)",
    ],
    "Machine Learning": [
        "Gradient_descent", "Overfitting", "Bias–variance_tradeoff",
        "Regularization_(mathematics)", "Support_vector_machine",
        "Random_forest", "Backpropagation", "Cross-validation_(statistics)",
    ],
}

# Fill these in with actual raw.githubusercontent.com CSV URLs from the
# company-wise LeetCode repos. Only Title/Difficulty columns are used —
# no problem statement text is ever pulled from these.
COMPANY_CSV_URLS = {
    # "Amazon": "https://raw.githubusercontent.com/<user>/<repo>/main/amazon/....csv",
    # "Google": "https://raw.githubusercontent.com/<user>/<repo>/main/google/....csv",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; college-project-scraper/1.0)"}


# ---------------------------------------------------------------------------
# 1. Codeforces — metadata via official API
# ---------------------------------------------------------------------------

def fetch_codeforces_metadata():
    """Pull the full CF problem list once, then bucket by our target tags."""
    resp = requests.get(CF_API, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "OK":
        raise RuntimeError(f"Codeforces API error: {data}")

    problems = data["result"]["problems"]
    buckets = {cat: [] for cat in TAG_MAP.values()}

    for p in problems:
        tags = [t.lower() for t in p.get("tags", [])]
        rating = p.get("rating")
        if rating is None:
            continue  # unrated problems have no reliable difficulty signal
        for cf_tag, category in TAG_MAP.items():
            if cf_tag in tags and len(buckets[category]) < PROBLEMS_PER_CATEGORY:
                buckets[category].append({
                    "contestId": p["contestId"],
                    "index": p["index"],
                    "name": p["name"],
                    "cf_tags": p.get("tags", []),
                    "rating": rating,
                    "category_hint": category,
                })
    return buckets


def difficulty_from_rating(rating):
    """Map Codeforces numeric rating to Easy/Medium/Hard."""
    if rating <= 1200:
        return "Easy"
    elif rating <= 1900:
        return "Medium"
    return "Hard"


# ---------------------------------------------------------------------------
# 2. Codeforces — actual page scrape + HTML cleaning
# ---------------------------------------------------------------------------

def fetch_problem_statement(problem):
    """Fetch a single CF problem page and extract clean statement text."""
    url = CF_PROBLEM_URL.format(contestId=problem["contestId"], index=problem["index"])
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {**problem, "url": url, "raw_text": None, "error": str(e)}

    soup = BeautifulSoup(resp.text, "html.parser")
    statement_div = soup.find("div", class_="problem-statement")

    if not statement_div:
        return {**problem, "url": url, "raw_text": None, "error": "no statement div found"}

    # Strip anything that isn't readable statement text
    for tag in statement_div(["script", "style"]):
        tag.decompose()

    raw_text = statement_div.get_text(separator="\n", strip=True)

    return {
        **problem,
        "source": "codeforces",
        "type": "coding",
        "url": url,
        "difficulty_hint": difficulty_from_rating(problem["rating"]),
        "company_hint": "General",   # CF problems have no real company signal
        "raw_text": raw_text,
        "error": None,
    }


def scrape_codeforces(buckets):
    all_problems = [p for cat_list in buckets.values() for p in cat_list]
    results = []
    print(f"Scraping {len(all_problems)} Codeforces problem pages...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_problem_statement, p): p for p in all_problems}
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            results.append(result)
            status = "FAILED" if result.get("error") else "OK"
            print(f"  [{i + 1}/{len(all_problems)}] {status}: {result['name']}"
                  + (f" — {result['error']}" if result.get("error") else ""))
            time.sleep(REQUEST_DELAY_SEC)

    return [r for r in results if r["raw_text"]]  # drop failures


# ---------------------------------------------------------------------------
# 3. Wikipedia — conceptual/bonus items (for domain-detection demo)
# ---------------------------------------------------------------------------

def fetch_wikipedia_intro(title):
    url = f"https://en.wikipedia.org/wiki/{title}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        return None, str(e)

    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.find("div", class_="mw-parser-output")
    if not content:
        return None, "no content div found"

    paragraphs = []
    for p in content.find_all("p", recursive=False):
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)
        if len(paragraphs) >= 4:  # intro is enough — this is just grounding text
            break

    return ("\n\n".join(paragraphs) or None), None


def scrape_wikipedia_concepts():
    results = []
    for domain, titles in WIKIPEDIA_CONCEPTS.items():
        for title in titles:
            text, error = fetch_wikipedia_intro(title)
            results.append({
                "source": "wikipedia",
                "type": "conceptual",
                "name": title.replace("_", " "),
                "domain_hint": domain,
                "url": f"https://en.wikipedia.org/wiki/{title}",
                "raw_text": text,
                "error": error,
            })
            print(f"  {'OK' if text else 'FAILED'}: {title}")
            time.sleep(REQUEST_DELAY_SEC)
    return [r for r in results if r["raw_text"]]


# ---------------------------------------------------------------------------
# 4. LeetCode company CSVs — metadata-only seeds (title/company/difficulty)
#    NOTE: no problem text is pulled from these — only public metadata columns.
# ---------------------------------------------------------------------------

def load_company_seeds():
    results = []
    for company, csv_url in COMPANY_CSV_URLS.items():
        try:
            resp = requests.get(csv_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  FAILED to load {company} CSV: {e}")
            continue

        reader = csv.DictReader(io.StringIO(resp.text))
        for row in reader:
            title = row.get("Title") or row.get("title")
            difficulty = row.get("Difficulty") or row.get("difficulty") or "Medium"
            if not title:
                continue
            results.append({
                "source": "leetcode_company_csv",
                "type": "coding_seed_only",   # no raw_text — title-only seed
                "name": title,
                "company_hint": company,
                "difficulty_hint": difficulty,
                "raw_text": None,
                "category_hint": None,  # left for classify.py to assign —
                                         # bias toward Backtracking here since
                                         # that's the category CF underrepresents
            })
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== Stage 1: Codeforces metadata ===")
    buckets = fetch_codeforces_metadata()
    for cat, items in buckets.items():
        print(f"  {cat}: {len(items)} candidates")

    print("\n=== Stage 1: Codeforces page scrape ===")
    cf_items = scrape_codeforces(buckets)

    print("\n=== Stage 1: Wikipedia conceptual bonus items ===")
    wiki_items = scrape_wikipedia_concepts()

    print("\n=== Stage 1: LeetCode company seed metadata ===")
    seed_items = load_company_seeds()
    if not COMPANY_CSV_URLS:
        print("  (skipped — fill in COMPANY_CSV_URLS with raw GitHub CSV links first)")

    all_items = cf_items + wiki_items + seed_items
    with open("raw_items.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Wrote {len(all_items)} raw items to raw_items.json")
    print(f"  Codeforces (real scrape): {len(cf_items)}")
    print(f"  Wikipedia (bonus, real scrape): {len(wiki_items)}")
    print(f"  LeetCode company seeds (metadata only): {len(seed_items)}")


if __name__ == "__main__":
    main()
