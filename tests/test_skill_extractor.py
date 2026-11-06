"""
Unit Tests for Skill Extraction Engine
"""

import unittest
from modules.skill_extractor import skill_extractor

class TestSkillExtractor(unittest.TestCase):
    def test_exact_matches(self):
        text = "Skilled in Python, Java, SQL, and Docker development."
        skills = skill_extractor.extract_skills(text)
        self.assertIn("Python", skills)
        self.assertIn("Java", skills)
        self.assertIn("SQL", skills)
        self.assertIn("Docker", skills)

    def test_alias_resolution(self):
        text = "Strong background in ML, DL, NLP, and K8s orchestration."
        skills = skill_extractor.extract_skills(text)
        self.assertIn("Machine Learning", skills)
        self.assertIn("Deep Learning", skills)
        self.assertIn("Natural Language Processing", skills)
        self.assertIn("Kubernetes", skills)

    def test_multi_word_skills(self):
        text = "Experience with Natural Language Processing, Spring Boot, and Computer Vision."
        skills = skill_extractor.extract_skills(text)
        self.assertIn("Natural Language Processing", skills)
        self.assertIn("Spring Boot", skills)
        self.assertIn("Computer Vision", skills)

    def test_avoid_false_positive_partial_matches(self):
        # 'C' should not match inside words like 'concept', 'accuracy', 'specific'
        text = "Focus on accuracy and clear concept of general mechanics."
        skills = skill_extractor.extract_skills(text)
        self.assertNotIn("C", skills)

    def test_c_and_cpp_differentiation(self):
        text_cpp = "Expert in C++ and C# software systems."
        skills_cpp = skill_extractor.extract_skills(text_cpp)
        self.assertIn("C++", skills_cpp)
        self.assertIn("C#", skills_cpp)
        self.assertNotIn("C", skills_cpp)

        text_c = "Solid background in C programming and algorithms."
        skills_c = skill_extractor.extract_skills(text_c)
        self.assertIn("C", skills_c)

if __name__ == "__main__":
    unittest.main()

