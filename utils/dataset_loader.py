"""
Dataset Integration Bridge for TalentRank AI
Seamlessly connects the platform to the workspace datasets:
- Dataset 1: Real PDF resumes and Resume.csv across 24 job domains
- Dataset 2: 1.74GB Job Descriptions dataset with curated presets and streaming chunked search
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from config import DATASET_1_DIR, DATASET_1_CSV, DATASET_1_PDF_DIR, DATASET_2_CSV, SAMPLE_DATA_DIR
from modules.resume_parser import resume_parser
from modules.job_parser import job_parser


class DatasetLoader:
    def __init__(self):
        self.dataset1_pdf_dir = DATASET_1_PDF_DIR
        self.dataset1_csv = DATASET_1_CSV
        self.dataset2_csv = DATASET_2_CSV
        self.curated_jobs_file = SAMPLE_DATA_DIR / "curated_jobs.json"

    # --- Dataset 1: Resumes ---
    def get_dataset1_categories(self) -> List[str]:
        """Returns the list of available resume categories in Dataset 1."""
        if self.dataset1_pdf_dir.exists():
            cats = [d.name for d in self.dataset1_pdf_dir.iterdir() if d.is_dir()]
            return sorted(cats)
        return []

    def load_resumes_from_pdfs(self, category: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Loads and parses actual PDF files from Dataset 1 for a given category.
        """
        cat_dir = self.dataset1_pdf_dir / category
        if not cat_dir.exists():
            return []

        pdf_files = list(cat_dir.glob("*.pdf"))[:limit]
        parsed_candidates = []

        for p in pdf_files:
            try:
                with open(p, "rb") as f:
                    file_bytes = f.read()
                res = resume_parser.parse_resume(p.name, file_bytes)
                if res.get("success"):
                    res["dataset_category"] = category
                    parsed_candidates.append(res)
            except Exception as e:
                continue

        return parsed_candidates

    def load_resumes_from_csv(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Loads resumes from Dataset 1 Resume.csv.
        """
        if not self.dataset1_csv.exists():
            return []

        try:
            # Read in chunks or nrows
            df = pd.read_csv(self.dataset1_csv, nrows=1000)
            if category and category != "All":
                df = df[df["Category"].str.upper() == category.upper()]

            sample_df = df.head(limit)
            candidates = []

            for _, row in sample_df.iterrows():
                resume_id = str(row.get("ID", "0"))
                raw_text = str(row.get("Resume_str", ""))
                cat = str(row.get("Category", "General"))
                filename = f"Resume_{cat}_{resume_id}.txt"

                # Parse plain text
                res = resume_parser.parse_resume(filename, raw_text.encode("utf-8"))
                if res.get("success"):
                    res["dataset_category"] = cat
                    candidates.append(res)

            return candidates
        except Exception:
            return []

    # --- Dataset 2: Job Descriptions ---
    def load_curated_jobs(self) -> List[Dict[str, Any]]:
        """Loads fast curated jobs extracted from Dataset 2."""
        if self.curated_jobs_file.exists():
            with open(self.curated_jobs_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def search_jobs(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Performs fast streaming search over the 1.74GB Dataset 2 using pandas chunksize.
        """
        if not self.dataset2_csv.exists():
            return self.load_curated_jobs()[:limit]

        query_clean = query.strip().lower()
        if not query_clean:
            return self.load_curated_jobs()[:limit]

        results = []
        try:
            # Stream in chunks of 5000 rows
            for chunk in pd.read_csv(self.dataset2_csv, chunksize=5000):
                match = chunk[
                    chunk["Job Title"].str.lower().str.contains(query_clean, na=False) |
                    chunk["Role"].str.lower().str.contains(query_clean, na=False) |
                    chunk["skills"].str.lower().str.contains(query_clean, na=False)
                ]
                for _, row in match.iterrows():
                    results.append({
                        "job_title": str(row.get("Job Title", "")).strip(),
                        "role": str(row.get("Role", "")).strip(),
                        "company": str(row.get("Company", "Confidential")).strip(),
                        "experience": str(row.get("Experience", "2 to 5 Years")).strip(),
                        "qualifications": str(row.get("Qualifications", "Bachelor Degree")).strip(),
                        "skills": str(row.get("skills", "")).strip(),
                        "responsibilities": str(row.get("Responsibilities", "")).strip(),
                        "description": str(row.get("Job Description", "")).strip()
                    })
                    if len(results) >= limit:
                        return results
            return results
        except Exception:
            # Fallback to searching curated jobs
            curated = self.load_curated_jobs()
            return [
                j for j in curated
                if query_clean in j["job_title"].lower() or query_clean in j["skills"].lower()
            ][:limit]


dataset_loader = DatasetLoader()
