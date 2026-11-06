"""
Explainable AI Module for TalentRank AI
Generates transparent, human-readable explanations of candidate match scores,
identifying key scoring drivers, skill strengths, gaps, and recruiter takeaways.
"""

from typing import Dict, Any, List


class ExplainabilityEngine:
    @staticmethod
    def generate_explanation(result: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates structured and narrative explainability reports for a candidate.
        """
        name = result.get("candidate_name", "Candidate")
        final_score = result.get("final_score", 0.0)
        rec = result.get("recommendation", "Needs Review")

        matched_req = result.get("matched_required", [])
        missing_req = result.get("missing_required", [])
        matched_pref = result.get("matched_preferred", [])
        missing_pref = result.get("missing_preferred", [])

        sim_score = result.get("similarity_score", 0.0)
        exp_score = result.get("experience_score", 0.0)
        edu_score = result.get("education_score", 0.0)
        cand_exp = result.get("candidate_exp", result.get("experience", 0.0))
        req_exp = job_data.get("minimum_experience", 0.0)

        # Build Key Strengths
        strengths = []
        if matched_req:
            strengths.append(f"Strong required skill alignment in: {', '.join(matched_req[:4])}")
        if matched_pref:
            strengths.append(f"Bonus skills matching preferred criteria: {', '.join(matched_pref[:3])}")
        if sim_score >= 60.0:
            strengths.append(f"High resume-to-job contextual text similarity ({sim_score:.1f}%)")
        if cand_exp >= req_exp and req_exp > 0:
            strengths.append(f"Meets or exceeds experience requirement ({cand_exp:.1f} yrs vs {req_exp:.1f} yrs required)")

        # Build Areas for Recruiter Verification (Gaps)
        gaps = []
        if missing_req:
            gaps.append(f"Mandatory skills not detected in resume: {', '.join(missing_req[:4])}")
        if missing_pref:
            gaps.append(f"Preferred skills not found: {', '.join(missing_pref[:3])}")
        if cand_exp < req_exp and req_exp > 0:
            gaps.append(f"Reported experience ({cand_exp:.1f} yrs) is below stated job requirement ({req_exp:.1f} yrs)")
        if sim_score < 40.0:
            gaps.append(f"Low semantic text overlap with job description ({sim_score:.1f}%)")

        # Score Breakdown Component Contributions
        w = result.get("weights_used", {
            "required_skills": 0.40,
            "similarity": 0.25,
            "preferred_skills": 0.15,
            "experience": 0.10,
            "education": 0.05,
            "keyword": 0.05
        })

        contributions = {
            "Required Skills": round(result.get("skill_score", 0.0) * w.get("required_skills", 0.40), 2),
            "Text Similarity": round(sim_score * w.get("similarity", 0.25), 2),
            "Preferred Skills": round(result.get("preferred_skill_score", 0.0) * w.get("preferred_skills", 0.15), 2),
            "Experience": round(exp_score * w.get("experience", 0.10), 2),
            "Education": round(edu_score * w.get("education", 0.05), 2),
            "Keyword Relevance": round(result.get("keyword_score", 0.0) * w.get("keyword", 0.05), 2)
        }

        # Top driving factor
        top_factor = max(contributions.items(), key=lambda x: x[1])

        # Summary narrative
        narrative = (
            f"{name} achieved an overall match score of {final_score:.1f}%, classified as '{rec}'. "
            f"The primary scoring driver was {top_factor[0]} (contributing +{top_factor[1]:.1f} pts). "
        )
        if matched_req:
            narrative += f"Successfully demonstrated {len(matched_req)} core required skills. "
        if missing_req:
            narrative += (
                f"Note: {len(missing_req)} required skill(s) were undetected in the resume text "
                f"({', '.join(missing_req[:3])}). Recruiter verification during interview screening is recommended."
            )

        return {
            "summary_narrative": narrative,
            "strengths": strengths if strengths else ["Profile provides foundational relevant experience"],
            "gaps": gaps if gaps else ["No major qualification deficits identified"],
            "contributions": contributions,
            "top_factor": top_factor[0],
            "recommendation_rationale": (
                f"Candidate exhibits {rec.lower()} characteristics. Use this score as decision-support guidance "
                f"alongside human recruiter review."
            )
        }


explainability_engine = ExplainabilityEngine()

