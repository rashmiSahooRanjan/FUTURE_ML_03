"""
Candidate Scoring Engine for TalentRank AI
Implements multi-factor weighted scoring combining required skills, preferred skills,
TF-IDF cosine similarity, experience alignment, education level, and keyword relevance.
"""

from typing import Dict, List, Any, Optional
from config import DEFAULT_WEIGHTS, THRESHOLD_STRONG_MATCH, THRESHOLD_GOOD_MATCH, THRESHOLD_PARTIAL_MATCH
from modules.similarity_engine import similarity_engine
from modules.text_preprocessing import preprocessor


class ScoringEngine:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self.validate_weights()

    def set_weights(self, new_weights: Dict[str, float]) -> bool:
        """Sets and validates custom weights."""
        total = sum(new_weights.values())
        if not (0.99 <= total <= 1.01):
            return False
        self.weights = new_weights
        return True

    def validate_weights(self):
        total = sum(self.weights.values())
        if not (0.99 <= total <= 1.01):
            # Normalize to 1.0
            self.weights = {k: v / total for k, v in self.weights.items()}

    def calculate_skill_scores(
        self, candidate_skills: List[str], required_skills: List[str], preferred_skills: List[str]
    ) -> Dict[str, Any]:
        """Calculates matched skills, missing skills, and skill match percentages."""
        candidate_set = set(s.lower() for s in candidate_skills)

        # Required skills
        matched_req = [s for s in required_skills if s.lower() in candidate_set]
        missing_req = [s for s in required_skills if s.lower() not in candidate_set]

        req_score = 100.0 if not required_skills else (len(matched_req) / len(required_skills)) * 100.0

        # Preferred skills
        matched_pref = [s for s in preferred_skills if s.lower() in candidate_set]
        missing_pref = [s for s in preferred_skills if s.lower() not in candidate_set]

        pref_score = 100.0 if not preferred_skills else (len(matched_pref) / len(preferred_skills)) * 100.0

        # Additional skills present in resume but not requested in JD
        requested_set = set(s.lower() for s in (required_skills + preferred_skills))
        additional_skills = [s for s in candidate_skills if s.lower() not in requested_set]

        return {
            "req_score": round(req_score, 2),
            "pref_score": round(pref_score, 2),
            "matched_required": matched_req,
            "missing_required": missing_req,
            "matched_preferred": matched_pref,
            "missing_preferred": missing_pref,
            "additional_skills": additional_skills,
            "all_matched": matched_req + matched_pref,
            "all_missing": missing_req + missing_pref
        }

    def calculate_experience_score(self, candidate_exp: float, required_exp: float) -> float:
        """
        Calculates experience compatibility score.
        If requirement is 0 or candidate meets/exceeds requirement -> 100.
        If missing or not mentioned -> 50 (neutral).
        Otherwise proportional score.
        """
        if required_exp <= 0.0:
            return 100.0
        if candidate_exp >= required_exp:
            return 100.0
        if candidate_exp <= 0.0:
            return 50.0  # Fair neutral score when unmentioned
        score = (candidate_exp / required_exp) * 100.0
        return round(min(100.0, score), 2)

    def calculate_education_score(self, candidate_edu: str, required_edu: str) -> float:
        """Calculates degree alignment score."""
        c_lower = candidate_edu.lower()
        r_lower = required_edu.lower()

        if c_lower in ["not specified", "not found", ""]:
            return 60.0  # Neutral baseline
        if any(deg in c_lower for deg in ["ph.d", "m.tech", "master", "mca", "mba"]):
            return 100.0
        if any(deg in c_lower for deg in ["b.tech", "b.e", "bachelor", "bca", "b.sc", "degree"]):
            return 90.0 if "master" not in r_lower else 75.0
        return 70.0

    def calculate_keyword_score(self, resume_cleaned: str, job_cleaned: str) -> float:
        """Calculates percentage of top job keywords appearing in resume text."""
        tokens = preprocessor.tokenize(job_cleaned)
        if not tokens:
            return 100.0

        # Frequency count to get top 20 key terms
        freq: Dict[str, int] = {}
        for t in tokens:
            if len(t) > 2:
                freq[t] = freq.get(t, 0) + 1

        top_keywords = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)[:25]
        if not top_keywords:
            return 100.0

        resume_tokens = set(preprocessor.tokenize(resume_cleaned))
        matched = [k for k in top_keywords if k in resume_tokens]
        score = (len(matched) / len(top_keywords)) * 100.0
        return round(score, 2)

    def get_recommendation(self, score: float) -> str:
        """Returns decision-support recommendation label."""
        if score >= THRESHOLD_STRONG_MATCH:
            return "Strong Match"
        elif score >= THRESHOLD_GOOD_MATCH:
            return "Good Match"
        elif score >= THRESHOLD_PARTIAL_MATCH:
            return "Partial Match"
        else:
            return "Needs Review"

    def score_candidate(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        similarity_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes complete multi-component scoring for a candidate against a job description.
        """
        candidate_skills = candidate_data.get("extracted_skills", [])
        required_skills = job_data.get("required_skills", [])
        preferred_skills = job_data.get("preferred_skills", [])

        # 1. Skill Scores
        skill_analysis = self.calculate_skill_scores(candidate_skills, required_skills, preferred_skills)

        # 2. Text Similarity (TF-IDF Cosine)
        if similarity_score is None:
            similarity_score = similarity_engine.compute_similarity(
                candidate_data.get("cleaned_text", "") or candidate_data.get("extracted_text", ""),
                job_data.get("cleaned_description", "") or job_data.get("description", "")
            )

        # 3. Experience Score
        candidate_exp = float(candidate_data.get("experience", 0.0))
        required_exp = float(job_data.get("minimum_experience", 0.0))
        exp_score = self.calculate_experience_score(candidate_exp, required_exp)

        # 4. Education Score
        candidate_edu = candidate_data.get("education", "Not Specified")
        required_edu = job_data.get("education_requirement", "Any Degree")
        edu_score = self.calculate_education_score(candidate_edu, required_edu)

        # 5. Keyword Relevance Score
        keyword_score = self.calculate_keyword_score(
            candidate_data.get("cleaned_text", ""),
            job_data.get("cleaned_description", "")
        )

        # Final Weighted Score Calculation
        w = self.weights
        final_score = (
            (skill_analysis["req_score"] * w["required_skills"]) +
            (similarity_score * w["similarity"]) +
            (skill_analysis["pref_score"] * w["preferred_skills"]) +
            (exp_score * w["experience"]) +
            (edu_score * w["education"]) +
            (keyword_score * w["keyword"])
        )
        final_score = round(float(final_score), 2)
        recommendation = self.get_recommendation(final_score)

        return {
            "candidate_id": candidate_data.get("candidate_id"),
            "candidate_name": candidate_data.get("candidate_name", "Unknown Candidate"),
            "resume_filename": candidate_data.get("resume_filename", ""),
            "final_score": final_score,
            "skill_score": skill_analysis["req_score"],
            "preferred_skill_score": skill_analysis["pref_score"],
            "similarity_score": similarity_score,
            "experience_score": exp_score,
            "education_score": edu_score,
            "keyword_score": keyword_score,
            "matched_skills": skill_analysis["all_matched"],
            "missing_skills": skill_analysis["all_missing"],
            "matched_required": skill_analysis["matched_required"],
            "missing_required": skill_analysis["missing_required"],
            "matched_preferred": skill_analysis["matched_preferred"],
            "missing_preferred": skill_analysis["missing_preferred"],
            "additional_skills": skill_analysis["additional_skills"],
            "recommendation": recommendation,
            "weights_used": self.weights.copy()
        }


scoring_engine = ScoringEngine()

