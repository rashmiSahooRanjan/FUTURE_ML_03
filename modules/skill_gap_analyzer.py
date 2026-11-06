"""
Skill Gap Analysis Module for TalentRank AI
Performs deep comparison between job requirements and candidate profiles,
generating coverage metrics, category breakdowns, and actionable upskilling insights.
"""

from typing import Dict, List, Any
import pandas as pd
from modules.skill_extractor import skill_extractor


class SkillGapAnalyzer:
    @staticmethod
    def analyze_skill_gap(
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates complete skill gap matrix, category coverage, and actionable insights.
        """
        cand_set = set(s.lower() for s in candidate_skills)
        matrix = []

        # Mandatory Skills analysis
        for s in required_skills:
            is_matched = s.lower() in cand_set
            cat = skill_extractor.skill_to_category.get(s.lower(), "Technical")
            matrix.append({
                "Skill": s,
                "Type": "Mandatory",
                "Status": "Matched" if is_matched else "Missing",
                "Category": cat
            })

        # Preferred Skills analysis
        for s in preferred_skills:
            is_matched = s.lower() in cand_set
            cat = skill_extractor.skill_to_category.get(s.lower(), "Technical")
            matrix.append({
                "Skill": s,
                "Type": "Preferred",
                "Status": "Matched" if is_matched else "Missing",
                "Category": cat
            })

        df_matrix = pd.DataFrame(matrix)

        # Additional Skills found in resume
        all_req_pref_lower = set(s.lower() for s in (required_skills + preferred_skills))
        additional_skills = [s for s in candidate_skills if s.lower() not in all_req_pref_lower]

        # Calculate category coverage
        category_coverage = {}
        for row in matrix:
            cat = row["Category"]
            if cat not in category_coverage:
                category_coverage[cat] = {"total": 0, "matched": 0}
            category_coverage[cat]["total"] += 1
            if row["Status"] == "Matched":
                category_coverage[cat]["matched"] += 1

        coverage_summary = []
        for cat, counts in category_coverage.items():
            pct = (counts["matched"] / counts["total"] * 100.0) if counts["total"] > 0 else 0.0
            coverage_summary.append({
                "Category": cat,
                "Matched": counts["matched"],
                "Total Required/Preferred": counts["total"],
                "Coverage (%)": round(pct, 1)
            })

        df_coverage = pd.DataFrame(coverage_summary)

        # Matched vs Missing counts
        total_req = len(required_skills)
        matched_req = sum(1 for row in matrix if row["Type"] == "Mandatory" and row["Status"] == "Matched")
        missing_req = total_req - matched_req

        total_pref = len(preferred_skills)
        matched_pref = sum(1 for row in matrix if row["Type"] == "Preferred" and row["Status"] == "Matched")
        missing_pref = total_pref - matched_pref

        return {
            "matrix_df": df_matrix,
            "coverage_df": df_coverage,
            "additional_skills": additional_skills,
            "total_mandatory": total_req,
            "matched_mandatory": matched_req,
            "missing_mandatory": missing_req,
            "mandatory_coverage_pct": round((matched_req / total_req * 100.0), 1) if total_req > 0 else 100.0,
            "total_preferred": total_pref,
            "matched_preferred": matched_pref,
            "missing_preferred": missing_pref,
            "preferred_coverage_pct": round((matched_pref / total_pref * 100.0), 1) if total_pref > 0 else 100.0,
        }


skill_gap_analyzer = SkillGapAnalyzer()
