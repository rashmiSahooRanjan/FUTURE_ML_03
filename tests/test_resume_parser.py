"""
Unit Tests for Resume Parser Module
"""

import unittest
from modules.resume_parser import resume_parser

class TestResumeParser(unittest.TestCase):
    def test_txt_parsing(self):
        sample_txt = """
        John Doe
        Email: john.doe@example.com
        Phone: +1 555-019-2834
        LinkedIn: linkedin.com/in/johndoe
        B.Tech in Computer Science with 4 years of experience.
        Proficient in Python, Machine Learning, SQL, and Docker.
        """
        res = resume_parser.parse_resume("john_doe_resume.txt", sample_txt.encode('utf-8'))
        self.assertTrue(res["success"])
        self.assertEqual(res["candidate_name"], "John Doe")
        self.assertEqual(res["email"], "john.doe@example.com")
        self.assertIn("Python", res["extracted_skills"])
        self.assertIn("Machine Learning", res["extracted_skills"])
        self.assertEqual(res["experience"], 4.0)

    def test_empty_document(self):
        empty_bytes = b""
        res = resume_parser.parse_resume("empty.txt", empty_bytes)
        self.assertFalse(res["success"])
        self.assertIn("OCR", res.get("error", ""))

    def test_file_hash_consistency(self):
        content = b"Candidate resume contents testing hash."
        hash1 = resume_parser.calculate_file_hash(content)
        hash2 = resume_parser.calculate_file_hash(content)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

if __name__ == "__main__":
    unittest.main()

