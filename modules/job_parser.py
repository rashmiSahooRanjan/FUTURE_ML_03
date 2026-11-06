"""
Job Description Parser Module for TalentRank AI
Extracts job roles, minimum experience requirements, educational qualifications,
and intelligently segments skills into Mandatory (Required) and Preferred skills.
"""

import re
from typing import Dict, List, Any, Tuple
from modules.skill_extractor import skill_extractor
from modules.text_preprocessing import preprocessor


class JobParser:
    def __init__(self):
        # Patterns for experience
        self.exp_pattern = re.compile(
            r'(?:minimum|at\s+least|requires?)?\s*(\d+(?:\.\d+)?)\s*(?:to|-)?\s*(\d+(?:\.\d+)?)?\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?',
            re.IGNORECASE
        )

        # Degree requirements
        self.degree_pattern = re.compile(
            r'\b(b\.?tech|m\.?tech|b\.?e\.?|m\.?e\.?|b\.?sc|m\.?sc|bca|mca|bba|mba|ph\.?d|bachelor(?:\'s)?|master(?:\'s)?|degree in computer science|engineering degree)\b',
            re.IGNORECASE
        )

        # Mandatory section cues
        self.mandatory_cues = [
            "must have", "required", "requirements", "essential", "minimum qualifications",
            "what you need", "qualifications", "core skills", "responsibilities"
        ]

        # Preferred section cues
        self.preferred_cues = [
            "preferred", "nice to have", "plus", "bonus", "desirable", "good to have",
            "preferred qualifications", "additional skills"
        ]

    def extract_minimum_experience(self, text: str) -> float:
        """Extracts required minimum years of experience."""
        matches = self.exp_pattern.findall(text)
        if matches:
            try:
                # First capture group is minimum
                for m in matches:
                    val = float(m[0])
                    if val <= 25:
                        return val
            except Exception:
                pass
        return 0.0

    def extract_education_requirement(self, text: str) -> str:
        """Extracts requested education level."""
        matches = self.degree_pattern.findall(text)
        if matches:
            unique = set(m.upper() if len(m) <= 5 else m.title() for m in matches)
            return ", ".join(sorted(unique))
        return "Bachelor's Degree or Equivalent"

    def segment_skills(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Segments extracted skills into Mandatory (Required) and Preferred skills
        by analyzing contextual sections.
        """
        all_skills = skill_extractor.extract_skills(text)
        if not all_skills:
            return [], []

        text_lower = text.lower()
        mandatory_skills = set()
        preferred_skills = set()

        # Split text into lines/paragraphs to find sections
        lines = text.split("\n")
        current_mode = "mandatory"  # Default assumption for listed skills

        for line in lines:
            line_lower = line.lower().strip()
            if any(cue in line_lower for cue in self.preferred_cues):
                current_mode = "preferred"
            elif any(cue in line_lower for cue in self.mandatory_cues):
                current_mode = "mandatory"

            line_skills = skill_extractor.extract_skills(line)
            for s in line_skills:
                if current_mode == "preferred":
                    preferred_skills.add(s)
                else:
                    mandatory_skills.add(s)

        # Remove overlap (mandatory takes precedence)
        preferred_skills = preferred_skills - mandatory_skills

        # If everything fell into preferred or mandatory was too sparse, balance reasonably
        if not mandatory_skills and preferred_skills:
            mandatory_skills = preferred_skills
            preferred_skills = set()
        elif len(mandatory_skills) == 0 and len(all_skills) > 0:
            # Default first 70% as required, remaining as preferred
            cutoff = max(1, int(len(all_skills) * 0.7))
            mandatory_skills = set(all_skills[:cutoff])
            preferred_skills = set(all_skills[cutoff:])

        return sorted(list(mandatory_skills)), sorted(list(preferred_skills))

    def parse_job(self, title: str, description: str, company: str = "Confidential") -> Dict[str, Any]:
        """Parses a job posting into structured features."""
        cleaned_desc = preprocessor.clean_text(description)
        min_exp = self.extract_minimum_experience(description)
        edu_req = self.extract_education_requirement(description)
        mandatory_skills, preferred_skills = self.segment_skills(description)

        return {
            "job_title": title,
            "company_name": company,
            "description": description,
            "cleaned_description": cleaned_desc,
            "required_skills": mandatory_skills,
            "preferred_skills": preferred_skills,
            "minimum_experience": min_exp,
            "education_requirement": edu_req,
            "all_extracted_skills": sorted(list(set(mandatory_skills + preferred_skills)))
        }


job_parser = JobParser()

