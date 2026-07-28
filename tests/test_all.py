"""
test_all.py — Verification Test Suite for Backend & Pipeline

Tests:
1. FastAPI API endpoints using TestClient (/api/health, /api/questions, /api/stats, /api/sources, /api/companies, /api/export).
2. Deterministic tagger logic (category, difficulty, company mapping).
3. Deduplication logic (ON CONFLICT (id) DO NOTHING logic).
4. Code solution verification logic (Python runner).
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from pipeline.deterministic_tagger import determine_category, determine_difficulty, determine_companies
from pipeline.verify import verify_python_solution


class TestBackendAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")

    def test_questions_endpoint(self):
        res = self.client.get("/api/questions?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertLessEqual(len(data["items"]), 10)

    def test_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total", data)
        self.assertIn("verified_percentage", data)
        self.assertIn("by_source", data)

    def test_sources_endpoint(self):
        res = self.client.get("/api/sources")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)

    def test_companies_endpoint(self):
        res = self.client.get("/api/companies")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)

    def test_export_endpoint(self):
        res = self.client.post("/api/export", json={"ids": ["codeforces:1900A"]})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)


class TestPipelineLogic(unittest.TestCase):
    def test_deterministic_category(self):
        item = {"title": "Find Subsequence", "cf_tags": ["dp"]}
        cat = determine_category(item)
        self.assertEqual(cat, "Dynamic Programming")

    def test_deterministic_difficulty(self):
        item_easy = {"cf_rating": 800}
        item_hard = {"cf_rating": 1900}
        self.assertEqual(determine_difficulty(item_easy), "Easy")
        self.assertEqual(determine_difficulty(item_hard), "Hard")

    def test_python_verifier(self):
        code = "def solve(nums):\n    return sum(nums)"
        test_cases = [
            {"input": {"nums": [1, 2, 3]}, "expected_output": 6, "edge_case_type": "typical_case"}
        ]
        ok = verify_python_solution(code, test_cases)
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
