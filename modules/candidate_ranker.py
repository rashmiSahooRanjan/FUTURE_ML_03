"""
Candidate Ranking Module for TalentRank AI
Ranks candidates in descending order with multi-tier tie-breaking,
provides filtering, pagination, and multi-candidate comparative alignment.
"""

from typing import List, Dict, Any, Optional
import pandas as pd


class CandidateRanker:
    @staticmethod
    def rank_candidates(scored_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks candidates by final score descending with intelligent tie-breaking:
        1. Final Score
        2. Required Skill Score
        3. TF-IDF Similarity Score
        4. Experience Score
        """
        sorted_candidates = sorted(
            scored_candidates,
            key=lambda x: (
                x.get("final_score", 0.0),
                x.get("skill_score", 0.0),
                x.get("similarity_score", 0.0),
                x.get("experience_score", 0.0)
            ),
            reverse=True
        )

        ranked = []
        for rank, cand in enumerate(sorted_candidates, start=1):
            cand_copy = cand.copy()
            cand_copy["rank"] = rank
            ranked.append(cand_copy)
        return ranked

    @staticmethod
    def filter_candidates(
        candidates: List[Dict[str, Any]],
        min_score: float = 0.0,
        max_score: float = 100.0,
        recommendation: Optional[str] = None,
        search_query: Optional[str] = None,
        skill_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filters ranked candidates based on user criteria."""
        filtered = []
        q = (search_query or "").strip().lower()
        sf = (skill_filter or "").strip().lower()

        for c in candidates:
            score = c.get("final_score", 0.0)
            if not (min_score <= score <= max_score):
                continue

            if recommendation and recommendation != "All":
                if c.get("recommendation") != recommendation:
                    continue

            if q:
                name = c.get("candidate_name", "").lower()
                fname = c.get("resume_filename", "").lower()
                if q not in name and q not in fname:
                    continue

            if sf:
                matched = [s.lower() for s in c.get("matched_skills", [])]
                all_skills = [s.lower() for s in c.get("candidate_all_skills", [])]
                if sf not in matched and sf not in all_skills:
                    continue

            filtered.append(c)
        return filtered

    @staticmethod
    def build_comparison_dataframe(selected_candidates: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Builds a side-by-side comparison DataFrame for up to 5 candidates.
        """
        rows = []
        for c in selected_candidates:
            rows.append({
                "Rank": c.get("rank", "-"),
                "Candidate Name": c.get("candidate_name", "Unknown"),
                "Final Match": f"{c.get('final_score', 0):.1f}%",
                "Recommendation": c.get("recommendation", "-"),
                "Req. Skills Matched": f"{len(c.get('matched_required', []))} skills",
                "Missing Req. Skills": ", ".join(c.get("missing_required", [])) or "None",
                "TF-IDF Similarity": f"{c.get('similarity_score', 0):.1f}%",
                "Experience Match": f"{c.get('experience_score', 0):.1f}%",
                "Education Score": f"{c.get('education_score', 0):.1f}%",
                "Keyword Score": f"{c.get('keyword_score', 0):.1f}%"
            })
        return pd.DataFrame(rows)


candidate_ranker = CandidateRanker()

