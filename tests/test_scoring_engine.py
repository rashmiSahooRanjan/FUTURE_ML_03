"""
Unit Tests for Scoring Engine
"""

import unittest
from modules.scoring_engine import scoring_engine

class TestScoringEngine(unittest.TestCase):
    def test_all_required_skills_matched(self):
        cand = ["Python", "SQL", "Docker"]
        req = ["Python", "SQL"]
        pref = ["Docker"]
        res = scoring_engine.calculate_skill_scores(cand, req, pref)
        self.assertEqual(res["req_score"], 100.0)
        self.assertEqual(res["pref_score"], 100.0)

    def test_partial_required_skills_matched(self):
        cand = ["Python"]
        req = ["Python", "Docker"]
        pref = []
        res = scoring_engine.calculate_skill_scores(cand, req, pref)
        self.assertEqual(res["req_score"], 50.0)

    def test_experience_scoring(self):
        # Exceeds requirement
        self.assertEqual(scoring_engine.calculate_experience_score(5.0, 3.0), 100.0)
        # Meets requirement
        self.assertEqual(scoring_engine.calculate_experience_score(3.0, 3.0), 100.0)
        # Below requirement
        self.assertEqual(scoring_engine.calculate_experience_score(1.5, 3.0), 50.0)
        # No requirement
        self.assertEqual(scoring_engine.calculate_experience_score(0.0, 0.0), 100.0)

    def test_weight_validation(self):
        valid_weights = {
            "required_skills": 0.40,
            "similarity": 0.25,
            "preferred_skills": 0.15,
            "experience": 0.10,
            "education": 0.05,
            "keyword": 0.05
        }
        self.assertTrue(scoring_engine.set_weights(valid_weights))

        invalid_weights = {"required_skills": 0.50, "similarity": 0.20}  # sums to 0.70
        self.assertFalse(scoring_engine.set_weights(invalid_weights))

    def test_recommendation_labels(self):
        self.assertEqual(scoring_engine.get_recommendation(85.0), "Strong Match")
        self.assertEqual(scoring_engine.get_recommendation(72.0), "Good Match")
        self.assertEqual(scoring_engine.get_recommendation(52.0), "Partial Match")
        self.assertEqual(scoring_engine.get_recommendation(30.0), "Needs Review")

if __name__ == "__main__":
    unittest.main()
