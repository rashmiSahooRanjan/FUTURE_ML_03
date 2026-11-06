"""
Resume Parser Module for TalentRank AI
Extracts text from PDF (PyMuPDF), DOCX (python-docx), and TXT files.
Extracts candidate contact details, experience, education, and links using boundary-aware regex.
Generates SHA-256 hashes to detect duplicates.
"""

import re
import io
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import fitz  # PyMuPDF
import docx

from modules.skill_extractor import skill_extractor
from modules.text_preprocessing import preprocessor


class ResumeParser:
    def __init__(self):
        # Email pattern
        self.email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

        # Phone pattern (supports international and Indian formats)
        self.phone_pattern = re.compile(
            r'(?:(?:\+|00)?\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{4,5}'
        )

        # Links patterns
        self.linkedin_pattern = re.compile(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+', re.IGNORECASE)
        self.github_pattern = re.compile(r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+', re.IGNORECASE)
        self.portfolio_pattern = re.compile(r'(?:https?:\/\/)?(?:www\.)?(?:portfolio|behance|medium|dribbble)\.[a-z]{2,5}\/[a-zA-Z0-9_-]+', re.IGNORECASE)

        # Education degree indicators
        self.degree_pattern = re.compile(
            r'\b(b\.?tech|m\.?tech|b\.?e\.?|m\.?e\.?|b\.?sc|m\.?sc|bca|mca|bba|mba|ph\.?d|bachelor(?:\'s)?|master(?:\'s)?|doctorate|diploma)\b',
            re.IGNORECASE
        )

        # Experience pattern (e.g., "5+ years", "3.5 years of experience", "2 yrs")
        self.exp_pattern = re.compile(
            r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?',
            re.IGNORECASE
        )

    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Computes SHA-256 hash of file content for duplicate detection."""
        return hashlib.sha256(file_bytes).hexdigest()

    def extract_text_from_pdf(self, file_bytes: bytes) -> Tuple[str, bool]:
        """
        Extracts text from PDF bytes using PyMuPDF.
        Returns: (text, is_scanned_or_empty)
        """
        text_content = []
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text_content.append(page.get_text() or "")
            full_text = "\n".join(text_content).strip()
            is_empty = len(full_text) < 20
            return full_text, is_empty
        except Exception as e:
            return f"Error extracting PDF: {str(e)}", True

    def extract_text_from_docx(self, file_bytes: bytes) -> Tuple[str, bool]:
        """
        Extracts text from DOCX bytes using python-docx.
        """
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text_content = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    text_content.extend([cell.text.strip() for cell in row.cells if cell.text.strip()])
            full_text = "\n".join(text_content).strip()
            return full_text, len(full_text) < 20
        except Exception as e:
            return f"Error extracting DOCX: {str(e)}", True

    def extract_text_from_txt(self, file_bytes: bytes) -> Tuple[str, bool]:
        """Extracts text from plain text file bytes."""
        try:
            text = file_bytes.decode('utf-8', errors='ignore').strip()
            return text, len(text) < 20
        except Exception as e:
            return f"Error extracting TXT: {str(e)}", True

    def extract_text(self, filename: str, file_bytes: bytes) -> Tuple[str, bool, Optional[str]]:
        """
        Dispatches file to appropriate parser based on file extension.
        Returns: (extracted_text, is_empty_or_scanned, error_message)
        """
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            text, is_empty = self.extract_text_from_pdf(file_bytes)
        elif ext in [".docx", ".doc"]:
            text, is_empty = self.extract_text_from_docx(file_bytes)
        elif ext == ".txt":
            text, is_empty = self.extract_text_from_txt(file_bytes)
        else:
            return "", True, f"Unsupported file extension: {ext}"

        if is_empty:
            return text, True, "Document appears scanned or contains only images. OCR is required."
        return text, False, None

    def extract_candidate_name(self, text: str, filename: str) -> str:
        """
        Extracts candidate name from the top lines of resume or falls back to filename stem.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            # Discard headers like 'RESUME', 'CURRICULUM VITAE', contact lines
            if re.search(r'\b(resume|curriculum vitae|cv|page|contact|email|phone)\b', line, re.IGNORECASE):
                continue
            # A candidate name is typically 2-4 alphabetic words
            words = line.split()
            if 1 <= len(words) <= 4 and all(re.match(r'^[A-Za-z\.\'-]+$', w) for w in words):
                return line.title()

        # Fallback to sanitized filename
        stem = Path(filename).stem
        cleaned_stem = re.sub(r'[^A-Za-z\s]', ' ', stem).strip()
        return cleaned_stem.title() if cleaned_stem else "Candidate"

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extracts email, phone, and professional profile URLs."""
        email_match = self.email_pattern.search(text)
        email = email_match.group(0) if email_match else "Not Found"

        # Search phone
        phones = self.phone_pattern.findall(text)
        phone = "Not Found"
        for p in phones:
            digits = re.sub(r'\D', '', p)
            if 9 <= len(digits) <= 13:
                phone = p.strip()
                break

        linkedin_match = self.linkedin_pattern.search(text)
        linkedin = linkedin_match.group(0) if linkedin_match else "Not Found"

        github_match = self.github_pattern.search(text)
        github = github_match.group(0) if github_match else "Not Found"

        portfolio_match = self.portfolio_pattern.search(text)
        portfolio = portfolio_match.group(0) if portfolio_match else "Not Found"

        # Location heuristic (looks for City, State or Location indicator)
        loc_match = re.search(r'(?:location|address|residence|city)[:\s]+([^\n,]+(?:,[^\n]+)?)', text, re.IGNORECASE)
        location = loc_match.group(1).strip() if loc_match else "Not Found"

        return {
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio,
            "location": location
        }

    def extract_education(self, text: str) -> str:
        """Extracts degrees and educational qualifications."""
        degrees = set(self.degree_pattern.findall(text))
        if degrees:
            # Capitalize standard degrees
            formatted = [d.upper() if len(d) <= 5 else d.title() for d in degrees]
            return ", ".join(sorted(formatted))
        return "Not Specified"

    def extract_experience_years(self, text: str) -> float:
        """
        Extracts estimated total years of professional experience.
        """
        matches = self.exp_pattern.findall(text)
        if matches:
            try:
                # Pick the highest realistic experience mentioned (e.g., <= 40 years)
                exp_values = [float(m) for m in matches if float(m) <= 40]
                if exp_values:
                    return max(exp_values)
            except Exception:
                pass
        return 0.0

    def parse_resume(self, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """
        Full end-to-end resume parsing pipeline.
        """
        file_hash = self.calculate_file_hash(file_bytes)
        raw_text, is_empty, error_msg = self.extract_text(filename, file_bytes)

        if is_empty and error_msg:
            return {
                "success": False,
                "resume_filename": filename,
                "resume_hash": file_hash,
                "error": error_msg,
                "raw_text": raw_text
            }

        cleaned_text = preprocessor.clean_text(raw_text)
        skills = skill_extractor.extract_skills(raw_text)
        contact = self.extract_contact_info(raw_text)
        candidate_name = self.extract_candidate_name(raw_text, filename)
        education = self.extract_education(raw_text)
        experience_years = self.extract_experience_years(raw_text)

        return {
            "success": True,
            "candidate_name": candidate_name,
            "email": contact["email"],
            "phone": contact["phone"],
            "location": contact["location"],
            "linkedin": contact["linkedin"],
            "github": contact["github"],
            "portfolio": contact["portfolio"],
            "resume_filename": filename,
            "resume_hash": file_hash,
            "extracted_text": raw_text,
            "cleaned_text": cleaned_text,
            "extracted_skills": skills,
            "education": education,
            "experience": experience_years
        }


resume_parser = ResumeParser()
