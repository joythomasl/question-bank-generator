"""
scrapers.py — Stage 1: Multi-Source Problem Extractor

Scrapes questions from Codeforces, CSES, GeeksforGeeks, LeetCode, HackerRank.
Returns items formatted for downstream deterministic tagging and LLM enrichment.
Handles per-source errors so single source failures do not crash the pipeline.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import json
from typing import List, Dict, Any, Tuple

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ---------------------------------------------------------------------------
# Codeforces Scraper
# ---------------------------------------------------------------------------
def scrape_codeforces(limit: int = 3, exclude_ids: set = None) -> List[Dict[str, Any]]:
    exclude_ids = exclude_ids or set()
    print(f"[Scraper] Fetching Codeforces metadata from API (limit: {limit})...")
    api_url = "https://codeforces.com/api/problemset.problems"
    res = requests.get(api_url, headers=REQUEST_HEADERS, timeout=15)
    if res.status_code != 200:
        raise Exception(f"Codeforces API error {res.status_code}")

    data = res.json()
    if data.get("status") != "OK":
        raise Exception(f"Codeforces API status not OK: {data.get('comment')}")

    problems = data["result"]["problems"]
    items = []

    for prob in problems:
        if len(items) >= limit:
            break

        contest_id = prob.get("contestId")
        index = prob.get("index")
        name = prob.get("name")
        rating = prob.get("rating")
        tags = prob.get("tags", [])

        if not contest_id or not index or not name:
            continue

        source_id = f"{contest_id}{index}"
        source_url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
        question_id = f"codeforces:{source_id}"

        if question_id in exclude_ids:
            continue

        statement_text = ""
        scraped_test_cases = []

        try:
            p_res = requests.get(source_url, headers=REQUEST_HEADERS, timeout=5)
            if p_res.status_code == 200:
                soup = BeautifulSoup(p_res.text, "html.parser")

                statement_div = soup.find("div", class_="problem-statement")
                if statement_div:
                    statement_copy = BeautifulSoup(str(statement_div), "html.parser")
                    sample_tests = statement_copy.find("div", class_="sample-tests")
                    if sample_tests:
                        sample_tests.decompose()
                    header = statement_copy.find("div", class_="header")
                    if header:
                        header.decompose()
                    statement_text = statement_copy.get_text(separator="\n").strip()

                sample_test_div = soup.find("div", class_="sample-test")
                if sample_test_div:
                    inputs = sample_test_div.find_all("div", class_="input")
                    outputs = sample_test_div.find_all("div", class_="output")
                    for inp_div, out_div in zip(inputs, outputs):
                        inp_pre = inp_div.find("pre")
                        out_pre = out_div.find("pre")
                        if inp_pre and out_pre:
                            inp_str = "\n".join([line for line in inp_pre.stripped_strings])
                            out_str = "\n".join([line for line in out_pre.stripped_strings])
                            scraped_test_cases.append({
                                "input": inp_str,
                                "expected_output": out_str,
                                "edge_case_type": "sample_case",
                                "origin": "scraped"
                            })
            time.sleep(0.2)
        except Exception:
            pass

        items.append({
            "id": question_id,
            "title": name,
            "source_site": "codeforces",
            "source_url": source_url,
            "source_id": source_id,
            "cf_tags": tags,
            "cf_rating": rating,
            "problem_statement": statement_text or f"Given {name}, solve the problem described at {source_url}.",
            "scraped_test_cases": scraped_test_cases,
            "partial_scrape": len(statement_text) < 50
        })

    return items


# ---------------------------------------------------------------------------
# CSES Scraper
# ---------------------------------------------------------------------------
def scrape_cses(limit: int = 3, exclude_ids: set = None) -> List[Dict[str, Any]]:
    exclude_ids = exclude_ids or set()
    print(f"[Scraper] Fetching CSES problemset list (limit: {limit})...")
    list_url = "https://cses.fi/problemset/list/"
    res = requests.get(list_url, headers=REQUEST_HEADERS, timeout=15)
    if res.status_code != 200:
        raise Exception(f"CSES list error {res.status_code}")

    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    current_section = "Introductory Problems"
    task_nodes = []

    content = soup.find("div", class_="content")
    if content:
        for elem in content.children:
            if elem.name == "h2":
                current_section = elem.get_text().strip()
            elif elem.name == "ul":
                for li in elem.find_all("li"):
                    a = li.find("a")
                    if a and "/problemset/task/" in a.get("href", ""):
                        href = a["href"]
                        task_id = href.split("/")[-1]
                        title = a.get_text().strip()
                        task_nodes.append((task_id, title, current_section))

    for task_id, title, section in task_nodes:
        if len(items) >= limit:
            break
        question_id = f"cses:{task_id}"
        if question_id in exclude_ids:
            continue

        source_url = f"https://cses.fi/problemset/task/{task_id}"
        statement_text = ""
        scraped_test_cases = []

        try:
            t_res = requests.get(source_url, headers=REQUEST_HEADERS, timeout=5)
            if t_res.status_code == 200:
                tsoup = BeautifulSoup(t_res.text, "html.parser")
                tcontent = tsoup.find("div", class_="content")
                if tcontent:
                    pres = tcontent.find_all("pre")
                    for i in range(0, len(pres) - 1, 2):
                        inp_str = pres[i].get_text().strip()
                        out_str = pres[i+1].get_text().strip()
                        scraped_test_cases.append({
                            "input": inp_str,
                            "expected_output": out_str,
                            "edge_case_type": "sample_case",
                            "origin": "scraped"
                        })
                    statement_text = tcontent.get_text(separator="\n").strip()
            time.sleep(0.2)
        except Exception:
            pass

        items.append({
            "id": question_id,
            "title": title,
            "source_site": "cses",
            "source_url": source_url,
            "source_id": task_id,
            "cses_section": section,
            "problem_statement": statement_text or f"Solve CSES problem: {title}.",
            "scraped_test_cases": scraped_test_cases,
            "partial_scrape": len(statement_text) < 50
        })

    return items


# ---------------------------------------------------------------------------
# GeeksforGeeks Scraper
# ---------------------------------------------------------------------------
def scrape_geeksforgeeks(limit: int = 3, exclude_ids: set = None) -> List[Dict[str, Any]]:
    exclude_ids = exclude_ids or set()
    print(f"[Scraper] Scraping GeeksforGeeks items (limit: {limit})...")
    gfg_slugs = [
        "subarray-with-given-sum-1587115621",
        "missing-number-in-array1416",
        "parenthesis-checker2705",
        "find-duplicates-in-an-array",
        "kadanes-algorithm-1587115620",
        "minimum-number-of-jumps-1587115620",
        "nth-node-from-end-of-linked-list",
        "detect-loop-in-linked-list",
        "reverse-a-linked-list",
        "left-view-of-binary-tree",
        "row-with-max-1s0011",
        "kth-smallest-element5635",
        "spirally-traversing-a-matrix-1587115621",
        "majority-element-1587115620",
        "sort-an-array-of-0s-1s-and-2s4231",
        "indexes-of-subarray-sum-1587115620",
        "leaders-in-an-array-1587115620",
        "equilibrium-point-1587115620"
    ]

    items = []
    for slug in gfg_slugs:
        if len(items) >= limit:
            break
        question_id = f"geeksforgeeks:{slug}"
        if question_id in exclude_ids:
            continue

        source_url = f"https://www.geeksforgeeks.org/problems/{slug}"
        title = slug.replace("-", " ").title()

        partial = True
        statement_text = f"GeeksforGeeks problem: {title}"
        scraped_test_cases = []

        try:
            res = requests.get(source_url, headers=REQUEST_HEADERS, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                body = soup.find("div", class_="entry-content") or soup.find("article")
                if body:
                    statement_text = body.get_text(separator="\n")[:800].strip()
                    partial = False
        except Exception:
            pass

        items.append({
            "id": question_id,
            "title": title,
            "source_site": "geeksforgeeks",
            "source_url": source_url,
            "source_id": slug,
            "problem_statement": statement_text,
            "scraped_test_cases": scraped_test_cases,
            "partial_scrape": partial
        })

    return items


# ---------------------------------------------------------------------------
# LeetCode Scraper (Public GraphQL - METADATA ONLY)
# ---------------------------------------------------------------------------
def scrape_leetcode(limit: int = 3, exclude_ids: set = None) -> List[Dict[str, Any]]:
    exclude_ids = exclude_ids or set()
    print(f"[Scraper] Fetching LeetCode metadata from public GraphQL (limit: {limit})...")
    graphql_url = "https://leetcode.com/graphql"
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
      problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip
        filters: $filters
      ) {
        questions: data {
          questionId
          title
          titleSlug
          difficulty
          topicTags {
            name
            slug
          }
        }
      }
    }
    """
    
    payload = {
        "query": query,
        "variables": {
            "categorySlug": "",
            "skip": 0,
            "limit": 50,
            "filters": {}
        }
    }

    res = requests.post(graphql_url, json=payload, headers=REQUEST_HEADERS, timeout=15)
    if res.status_code != 200:
        raise Exception(f"LeetCode GraphQL status {res.status_code}")

    data = res.json()
    questions = data.get("data", {}).get("problemsetQuestionList", {}).get("questions", [])
    items = []

    for q in questions:
        if len(items) >= limit:
            break
        title = q.get("title")
        slug = q.get("titleSlug")
        difficulty = q.get("difficulty")
        topic_tags = [t.get("name") for t in q.get("topicTags", []) if t.get("name")]

        if not slug or not title:
            continue

        question_id = f"leetcode:{slug}"
        if question_id in exclude_ids:
            continue

        source_url = f"https://leetcode.com/problems/{slug}/"

        items.append({
            "id": question_id,
            "title": title,
            "source_site": "leetcode",
            "source_url": source_url,
            "source_id": slug,
            "lc_difficulty": difficulty,
            "lc_topic_tags": topic_tags,
            "problem_statement": None,
            "scraped_test_cases": [],
            "partial_scrape": False
        })

    return items


# ---------------------------------------------------------------------------
# HackerRank Scraper (Best Effort)
# ---------------------------------------------------------------------------
def scrape_hackerrank(limit: int = 3, exclude_ids: set = None) -> List[Dict[str, Any]]:
    exclude_ids = exclude_ids or set()
    print(f"[Scraper] Attempting HackerRank fetch (limit: {limit})...")
    url = f"https://www.hackerrank.com/rest/contests/master/tracks/algorithms/challenges?offset=0&limit=50"
    
    res = requests.get(url, headers=REQUEST_HEADERS, timeout=10)
    if res.status_code != 200:
        raise Exception(f"HackerRank API return status {res.status_code}")

    data = res.json()
    models = data.get("models", [])
    if not models:
        raise Exception("HackerRank returned empty problem list")

    items = []
    for model in models:
        if len(items) >= limit:
            break
        slug = model.get("slug")
        title = model.get("name")
        if not slug or not title:
            continue

        question_id = f"hackerrank:{slug}"
        if question_id in exclude_ids:
            continue

        source_url = f"https://www.hackerrank.com/challenges/{slug}/problem"

        items.append({
            "id": question_id,
            "title": title,
            "source_site": "hackerrank",
            "source_url": source_url,
            "source_id": slug,
            "problem_statement": model.get("preview", f"HackerRank challenge: {title}"),
            "scraped_test_cases": [],
            "partial_scrape": False
        })

    return items


# ---------------------------------------------------------------------------
# Master Scrape Orchestrator
# ---------------------------------------------------------------------------
def scrape_all_sources(limit_per_source: int = 3, exclude_ids: set = None) -> Tuple[List[Dict[str, Any]], List[str]]:
    exclude_ids = exclude_ids or set()
    all_items = []
    failed_sources = []

    sources = [
        ("codeforces", lambda: scrape_codeforces(limit=limit_per_source, exclude_ids=exclude_ids)),
        ("cses", lambda: scrape_cses(limit=limit_per_source, exclude_ids=exclude_ids)),
        ("geeksforgeeks", lambda: scrape_geeksforgeeks(limit=limit_per_source, exclude_ids=exclude_ids)),
        ("leetcode", lambda: scrape_leetcode(limit=limit_per_source, exclude_ids=exclude_ids)),
        ("hackerrank", lambda: scrape_hackerrank(limit=limit_per_source, exclude_ids=exclude_ids)),
    ]

    for name, scraper_fn in sources:
        try:
            items = scraper_fn()
            all_items.extend(items)
            print(f"[Scraper] [OK] {name}: Scraped {len(items)} items.")
        except Exception as e:
            print(f"[Scraper] [FAIL] {name} failed: {e}")
            failed_sources.append(name)

    return all_items[:15], failed_sources

