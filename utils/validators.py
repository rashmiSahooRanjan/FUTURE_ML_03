"""
Validation Utilities for TalentRank AI
Validates file formats, file sizes, weight distributions, and text inputs.
"""

from typing import Dict, Tuple, List
from pathlib import Path
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB

class Validator:
    @staticmethod
    def validate_file(filename: str, file_size_bytes: int) -> Tuple[bool, str]:
        """Validates file extension and size constraints."""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Unsupported file type '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"

        size_mb = file_size_bytes / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            return False, f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit ({MAX_FILE_SIZE_MB} MB)."

        return True, ""

    @staticmethod
    def validate_weights(weights: Dict[str, float]) -> Tuple[bool, str]:
        """Validates that scoring weights sum to 100% (or 1.0) with tolerance."""
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            pct = total * 100
            return False, f"Scoring weights must sum to 100%. Current sum: {pct:.1f}%."
        return True, ""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitizes text by stripping harmful characters."""
        if not text:
            return ""
        return text.strip()


validator = Validator()
