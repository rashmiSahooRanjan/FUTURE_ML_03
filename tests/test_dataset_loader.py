"""
Unit Tests for Dataset Loader Module
Validates integration with Dataset 1 (Resumes) and Dataset 2 (Job Descriptions).
"""

import unittest
from utils.dataset_loader import dataset_loader

class TestDatasetLoader(unittest.TestCase):
    def test_get_dataset1_categories(self):
        categories = dataset_loader.get_dataset1_categories()
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        self.assertIn("INFORMATION-TECHNOLOGY", categories)

    def test_load_curated_jobs(self):
        jobs = dataset_loader.load_curated_jobs()
        self.assertIsInstance(jobs, list)
        self.assertGreater(len(jobs), 0)
        first_job = jobs[0]
        self.assertIn("job_title", first_job)
        self.assertIn("description", first_job)

    def test_search_jobs(self):
        results = dataset_loader.search_jobs("Developer", limit=3)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)
        if results:
            self.assertIn("job_title", results[0])

if __name__ == "__main__":
    unittest.main()
