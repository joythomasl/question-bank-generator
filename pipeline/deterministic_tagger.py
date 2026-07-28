"""
deterministic_tagger.py — Stage 2: LLM-Free Tagging & Classification

Performs 100% deterministic classification, difficulty rating, and company tagging:
  1. Category classification from source tags / sections + keyword rules fallback.
  2. Difficulty rating from CF rating buckets, LC difficulty, CSES position.
  3. Company tagging by matching problem titles/slugs against company CSV data.
"""

import requests
import csv
import io
import re
from typing import List, Dict, Any

# Map of GitHub CSV URLs for company question lists
COMPANY_CSV_URLS = {
    "AMD": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/AMD/5.%20All.csv",
    "Adobe": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Adobe/5.%20All.csv",
    "Amazon": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Amazon/5.%20All.csv",
    "Apple": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Apple/5.%20All.csv",
    "Bloomberg": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Bloomberg/5.%20All.csv",
    "Google": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Google/5.%20All.csv",
    "Meta": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Meta/5.%20All.csv",
    "Microsoft": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Microsoft/5.%20All.csv",
    "Nvidia": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Nvidia/5.%20All.csv",
    "Oracle": "https://raw.githubusercontent.com/liquidslr/leetcode-company-wise-problems/refs/heads/main/Oracle/5.%20All.csv",
}

# Cache for company title mappings: title_lower -> set of companies
_company_map_cache = None

def load_company_map() -> Dict[str, List[str]]:
    global _company_map_cache
    if _company_map_cache is not None:
        return _company_map_cache

    print("[Tagger] Loading company question mappings from GitHub CSVs...")
    mapping: Dict[str, List[str]] = {}

    for company, url in COMPANY_CSV_URLS.items():
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                reader = csv.DictReader(io.StringIO(res.text))
                for row in reader:
                    title = row.get("Title") or row.get("title") or row.get("name")
                    if title:
                        clean_title = title.strip().lower()
                        if clean_title not in mapping:
                            mapping[clean_title] = []
                        if company not in mapping[clean_title]:
                            mapping[clean_title].append(company)
        except Exception as e:
            print(f"  Warning: Failed to fetch CSV for {company}: {e}")

    _company_map_cache = mapping
    print(f"[Tagger] Loaded mappings for {len(mapping)} problem titles.")
    return _company_map_cache


CATEGORY_TAG_MAP = {
    "dp": "Dynamic Programming",
    "dynamic programming": "Dynamic Programming",
    "backtracking": "Backtracking",
    "greedy": "Greedy",
    "divide and conquer": "Divide and Conquer",
    "two pointers": "Two Pointers",
}

KEYWORD_CATEGORY_RULES = [
    (r"\b(dp|subsequence|knapsack|memoization)\b", "Dynamic Programming"),
    (r"\b(backtrack|n-queens|sudoku|permutation|combination)\b", "Backtracking"),
    (r"\b(greedy|interval|scheduling)\b", "Greedy"),
    (r"\b(divide and conquer|binary search|merge sort)\b", "Divide and Conquer"),
    (r"\b(two pointer|pointers|sliding window)\b", "Two Pointers"),
]


def determine_category(item: Dict[str, Any]) -> str:
    # 1. From source tags
    source_tags = []
    if item.get("cf_tags"):
        source_tags.extend([t.lower() for t in item["cf_tags"]])
    if item.get("lc_topic_tags"):
        source_tags.extend([t.lower() for t in item["lc_topic_tags"]])
    if item.get("cses_section"):
        source_tags.append(item["cses_section"].lower())

    for tag in source_tags:
        for key, cat in CATEGORY_TAG_MAP.items():
            if key in tag:
                return cat

    # 2. Keyword fallback on title + problem statement
    text = (item.get("title", "") + " " + (item.get("problem_statement") or "")).lower()
    for pattern, cat in KEYWORD_CATEGORY_RULES:
        if re.search(pattern, text):
            return cat

    return "Dynamic Programming"  # Default fallback category


def determine_difficulty(item: Dict[str, Any]) -> str:
    # 1. Codeforces rating
    if item.get("cf_rating"):
        r = item["cf_rating"]
        if r < 1200:
            return "Easy"
        elif r <= 1600:
            return "Medium"
        else:
            return "Hard"

    # 2. LeetCode difficulty
    if item.get("lc_difficulty"):
        d = item["lc_difficulty"].upper()
        if "EASY" in d:
            return "Easy"
        elif "HARD" in d:
            return "Hard"
        return "Medium"

    # 3. CSES section
    if item.get("cses_section"):
        sec = item["cses_section"].lower()
        if "introductory" in sec:
            return "Easy"
        elif "advanced" in sec or "additional" in sec:
            return "Hard"
        return "Medium"

    return "Medium"


def determine_companies(title: str, company_map: Dict[str, List[str]]) -> List[str]:
    if not title:
        return []
    clean = title.strip().lower()
    return company_map.get(clean, [])


def tag_item(item: Dict[str, Any], company_map: Dict[str, List[str]]) -> Dict[str, Any]:
    category = item.get("category") or determine_category(item)
    difficulty = item.get("difficulty") or determine_difficulty(item)
    companies = item.get("companies") or determine_companies(item.get("title", ""), company_map)

    return {
        **item,
        "category": category,
        "difficulty": difficulty,
        "companies": companies,
    }


def tag_all_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    company_map = load_company_map()
    tagged = [tag_item(item, company_map) for item in items]
    print(f"[Tagger] Successfully tagged {len(tagged)} items.")
    return tagged
