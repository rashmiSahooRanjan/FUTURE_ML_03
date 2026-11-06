"""
Unit Tests for Candidate Ranker Module
"""

import unittest
from modules.candidate_ranker import candidate_ranker

class TestCandidateRanker(unittest.TestCase):
    def test_descending_ranking(self):
        candidates = [
            {"candidate_name": "Alice", "final_score": 75.0, "skill_score": 80.0},
            {"candidate_name": "Bob", "final_score": 92.5, "skill_score": 90.0},
            {"candidate_name": "Charlie", "final_score": 60.0, "skill_score": 50.0}
        ]
        ranked = candidate_ranker.rank_candidates(candidates)
        self.assertEqual(ranked[0]["candidate_name"], "Bob")
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertEqual(ranked[1]["candidate_name"], "Alice")
        self.assertEqual(ranked[1]["rank"], 2)
        self.assertEqual(ranked[2]["candidate_name"], "Charlie")
        self.assertEqual(ranked[2]["rank"], 3)

    def test_tie_breaking(self):
        candidates = [
            {"candidate_name": "Cand1", "final_score": 80.0, "skill_score": 70.0, "similarity_score": 60.0, "experience_score": 50.0},
            {"candidate_name": "Cand2", "final_score": 80.0, "skill_score": 90.0, "similarity_score": 50.0, "experience_score": 50.0}
        ]
        ranked = candidate_ranker.rank_candidates(candidates)
        # Cand2 has higher skill score so should win tie
        self.assertEqual(ranked[0]["candidate_name"], "Cand2")

if __name__ == "__main__":
    unittest.main()

