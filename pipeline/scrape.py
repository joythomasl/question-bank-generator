"""
scrape.py — Stage 1: Data Extraction

Pulls raw problem data from:
  1. Codeforces (official API for metadata + tags/rating, BeautifulSoup for
     the actual problem statement HTML) — this is the primary, real scrape.
  2. Wikipedia articles on OS/ML concepts — raw text used to demonstrate the
     "conceptual question" bonus-detection path in classify.py.
  3. A public LeetCode company-wise CSV (from GitHub) — used ONLY for
     (title, company, difficulty) seed metadata, never for problem text.

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
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CF_API = "https://codeforces.com/api/problemset.problems"
CF_PROBLEM_URL = "https://codeforces.com/problemset/problem/{contestId}/{index}"

TAG_MAP = {
    "dp": "Dynamic Programming",
    "greedy": "Greedy",
    "divide and conquer": "Divide and Conquer",
    "two pointers": "Two Pointers",
}

PROBLEMS_PER_CATEGORY = 120
REQUEST_DELAY_SEC = 0.6          # delay between Codeforces page fetches
WIKI_REQUEST_DELAY_SEC = 1.5     # gentler delay for Wikipedia's API
MAX_WORKERS = 2                   # concurrent CF page fetches
RAW_ITEMS_PATH = "raw_items.json"

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

COMPANY_CSV_URLS = {"AMD": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/AMD/5.%20All.csv",
    "Accenture": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Accenture/5.%20All.csv",
    "Acko": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Acko/5.%20All.csv",
    "Adobe": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Adobe/5.%20All.csv",
    "Agoda": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Agoda/5.%20All.csv",
    "Airbnb": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Airbnb/5.%20All.csv",
    "Airbus SE": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Airbus%20SE/5.%20All.csv",
    "Airtel": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Airtel/5.%20All.csv",
    "Alibaba": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Alibaba/5.%20All.csv",
    "Amazon": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Amazon/5.%20All.csv",
    "American Express": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/American%20Express/5.%20All.csv",
    "Apollo.io": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Apollo.io/5.%20All.csv",
    "Apple": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Apple/5.%20All.csv",
    "Atlassian": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Atlassian/5.%20All.csv",
    "Audible": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Audible/5.%20All.csv",
    "Aurora": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Aurora/5.%20All.csv",
    "Autodesk": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Autodesk/5.%20All.csv",
    "Axon": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Axon/5.%20All.csv",
    "Bank of America": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Bank%20of%20America/5.%20All.csv",
    "BitGo": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/BitGo/5.%20All.csv",
    "BlackRock": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/BlackRock/5.%20All.csv",
    "Bloomberg": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Bloomberg/5.%20All.csv",
    "Booking.com": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Booking.com/5.%20All.csv",
    "CRED": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/CRED/5.%20All.csv",
    "Cadence": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Cadence/5.%20All.csv",
    "Capgemini": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Capgemini/5.%20All.csv",
    "Cisco": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Cisco/5.%20All.csv",
    "Cleartrip": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Cleartrip/5.%20All.csv",
    "Cognizant": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Cognizant/5.%20All.csv",
    "Coursera": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Coursera/5.%20All.csv",
    "CrowdStrike": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/CrowdStrike/5.%20All.csv",
    "delhivery":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Delhivery/5.%20All.csv", "Dell":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Dell/5.%20All.csv","Deloitte":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Deloitte/5.%20All.csv","Disney":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Disney/5.%20All.csv","Dream11":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Dream11/5.%20All.csv","Duolingo":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Duolingo/5.%20All.csv","Fiverr":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Fiverr/5.%20All.csv","Flipkart":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Flipkart/5.%20All.csv","GoDaddy":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/GoDaddy/5.%20All.csv","Goldman Sachs":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Goldman%20Sachs/5.%20All.csv","Google":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Google/5.%20All.csv","Grammarly":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Grammarly/5.%20All.csv","Groww":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Groww/5.%20All.csv","HCL":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/HCL/5.%20All.csv",
"HP":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/HP/5.%20All.csv","Hulu":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Hulu/5.%20All.csv","IBM":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/IBM/5.%20All.csv","Infosys":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Infosys/5.%20All.csv","Intel":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Intel/5.%20All.csv","JP Morgan":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/J.P.%20Morgan/5.%20All.csv","Larsen & Toubro":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Larsen%20%26%20Toubro/5.%20All.csv","Lenskart":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Lenskart/5.%20All.csv","LinkedIn":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/LinkedIn/5.%20All.csv","MakeMyTrip":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/MakeMyTrip/5.%20All.csv","Mastercard":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Mastercard/5.%20All.csv",
"McKinsey & Company":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/McKinsey/5.%20All.csv","Meta":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Meta/5.%20All.csv","Microsoft":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Microsoft/5.%20All.csv","MongoDB":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/MongoDB/5.%20All.csv","Morgan Stanley":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Morgan%20Stanley/5.%20All.csv","Myntra":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Myntra/5.%20All.csv","Netflix":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Netflix/5.%20All.csv","Nike":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Nike/5.%20All.csv",
"Nvidia": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Nvidia/5.%20All.csv",
    "OpenAI":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/OpenAI/5.%20All.csv",
    "Oracle":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Oracle/5.%20All.csv",
    "Paypal": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/PayPal/5.%20All.csv",
    "Paytm":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Paytm/5.%20All.csv",
    "PhonePe":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/PhonePe/5.%20All.csv",
    "Pinterest": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Pinterest/5.%20All.csv",
    "Qualcomm":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Qualcomm/5.%20All.csv",
    "Quora":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Quora/5.%20All.csv",
    "Roblox": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Roblox/5.%20All.csv",
    "Salesforce":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Salesforce/5.%20All.csv",
    "Samsung":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Samsung/5.%20All.csv",
    "Siemens": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Siemens/5.%20All.csv",
    "Sony":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Sony/5.%20All.csv",
    "Spotify":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Spotify/5.%20All.csv",
    "Swiggy": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Swiggy/5.%20All.csv",
    "Tech Mahindra":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Tech%20Mahindra/5.%20All.csv",
    "Tesla":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Tesla/5.%20All.csv",
    "Trilogy": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Trilogy/5.%20All.csv",
    "Uber":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Uber/5.%20All.csv",
    "Visa":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Visa/5.%20All.csv",
    "Walmart Labs": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Walmart%20Labs/5.%20All.csv",
    "Wells Fargo":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Wells%20Fargo/5.%20All.csv",
    "Huawei":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Huawei/5.%20All.csv",
    "Wipro": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Wipro/5.%20All.csv",
    "X":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/X/5.%20All.csv",
    "Yahoo":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Yahoo/5.%20All.csv",
    "Zepto": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Zepto/5.%20All.csv",
    "Zoho":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Zoho/5.%20All.csv",
    "Zomato":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Zomato/5.%20All.csv",
    "Zoom": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/Zoom/5.%20All.csv",
    "blinkit":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/blinkit/5.%20All.csv",
    "ebay":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/eBay/5.%20All.csv",
    "Jio": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/jio/5.%20All.csv",
    "Razorpay":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/razorpay/5.%20All.csv",
    "TCS":"https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/ff477f5d870ffbaeaa9728a152bb3d07d2d207f6/tcs/5.%20All.csv"}

# Wikimedia's API policy asks for a descriptive User-Agent with contact info —
# swap in your actual email or repo URL below.
HEADERS = {
    "User-Agent": "college-question-bank-project/1.0 (educational use; contact: your-email@example.com)"
}


# ---------------------------------------------------------------------------
# 1. Codeforces — metadata via official API
# ---------------------------------------------------------------------------

def fetch_codeforces_metadata():
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
            continue
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
    if rating <= 1200:
        return "Easy"
    elif rating <= 1900:
        return "Medium"
    return "Hard"


# ---------------------------------------------------------------------------
# 2. Codeforces — page scrape with retry-on-transient-error
# ---------------------------------------------------------------------------

def fetch_problem_statement(problem, max_retries=3):
    """Fetch a single CF problem page, retrying on 502/503/429 with backoff."""
    url = CF_PROBLEM_URL.format(contestId=problem["contestId"], index=problem["index"])
    resp = None
    last_error = None

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code in (502, 503, 429):
                last_error = f"{resp.status_code} server error (transient)"
                resp = None
                time.sleep((attempt + 1) * 3)
                continue
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            last_error = str(e)
            resp = None
            time.sleep((attempt + 1) * 3)

    if resp is None:
        return {**problem, "url": url, "raw_text": None, "error": last_error}

    soup = BeautifulSoup(resp.text, "html.parser")
    statement_div = soup.find("div", class_="problem-statement")
    if not statement_div:
        return {**problem, "url": url, "raw_text": None, "error": "no statement div found"}

    for tag in statement_div(["script", "style"]):
        tag.decompose()

    raw_text = statement_div.get_text(separator="\n", strip=True)

    return {
        **problem,
        "source": "codeforces",
        "type": "coding",
        "url": url,
        "difficulty_hint": difficulty_from_rating(problem["rating"]),
        "company_hint": "General",
        "raw_text": raw_text,
        "error": None,
    }


def load_existing_cf_results():
    """Resume support — skip pages that already succeeded on a previous run."""
    try:
        with open(RAW_ITEMS_PATH, encoding="utf-8") as f:
            existing = json.load(f)
    except FileNotFoundError:
        return {}

    cf_existing = {}
    for item in existing:
        if item.get("source") == "codeforces" and item.get("raw_text"):
            cf_existing[(item["contestId"], item["index"])] = item
    return cf_existing


def scrape_codeforces(buckets, existing=None):
    existing = existing or {}
    all_problems = [p for cat_list in buckets.values() for p in cat_list]

    to_fetch, already_done = [], []
    for p in all_problems:
        key = (p["contestId"], p["index"])
        if key in existing:
            already_done.append(existing[key])
        else:
            to_fetch.append(p)

    print(f"Reusing {len(already_done)} previously-scraped pages, "
          f"fetching {len(to_fetch)} new/retried ones...")

    results = list(already_done)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_problem_statement, p): p for p in to_fetch}
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            results.append(result)
            status = "FAILED" if result.get("error") else "OK"
            print(f"  [{i + 1}/{len(to_fetch)}] {status}: {result['name']}"
                  + (f" — {result['error']}" if result.get("error") else ""))
            time.sleep(REQUEST_DELAY_SEC)

    return [r for r in results if r["raw_text"]]


# ---------------------------------------------------------------------------
# 3. Wikipedia — REST summary API, with 429 backoff
# ---------------------------------------------------------------------------

def fetch_wikipedia_intro(title, max_retries=3):
    encoded_title = quote(title, safe="_()")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", (attempt + 1) * 5))
                time.sleep(retry_after)
                continue
            resp.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                return None, str(e)
            time.sleep((attempt + 1) * 3)
            continue

        try:
            data = resp.json()
        except ValueError as e:
            return None, f"non-JSON response: {e}"

        extract = data.get("extract")
        if not extract:
            return None, f"no extract field in response (keys: {list(data.keys())})"
        return extract, None

    return None, "exhausted retries (429 Too Many Requests)"


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
            status = "FAILED" if error else "OK"
            print(f"  {status}: {title}" + (f" — {error}" if error else ""))
            time.sleep(WIKI_REQUEST_DELAY_SEC)
    return [r for r in results if r["raw_text"]]


# ---------------------------------------------------------------------------
# 4. LeetCode company CSVs — metadata-only seeds
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
                "type": "coding_seed_only",
                "name": title,
                "company_hint": company,
                "difficulty_hint": difficulty,
                "raw_text": None,
                "category_hint": None,
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

    existing = load_existing_cf_results()

    print("\n=== Stage 1: Codeforces page scrape ===")
    cf_items = scrape_codeforces(buckets, existing=existing)

    print("\n=== Stage 1: Wikipedia conceptual bonus items ===")
    wiki_items = scrape_wikipedia_concepts()

    print("\n=== Stage 1: LeetCode company seed metadata ===")
    seed_items = load_company_seeds()
    if not COMPANY_CSV_URLS:
        print("  (skipped — fill in COMPANY_CSV_URLS with raw GitHub CSV links first)")

    all_items = cf_items + wiki_items + seed_items
    with open(RAW_ITEMS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Wrote {len(all_items)} raw items to {RAW_ITEMS_PATH}")
    print(f"  Codeforces (real scrape): {len(cf_items)}")
    print(f"  Wikipedia (bonus, real scrape): {len(wiki_items)}")
    print(f"  LeetCode company seeds (metadata only): {len(seed_items)}")


if __name__ == "__main__":
    main()