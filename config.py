"""
TalentRank AI - Configuration Module
Defines system constants, default scoring weights, paths, and color themes.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
DB_PATH = DATABASE_DIR / "talentrank.db"
ASSETS_DIR = BASE_DIR / "assets"
SAMPLE_DATA_DIR = DATA_DIR / "sample_data"
SKILLS_FILE = DATA_DIR / "skills_dictionary.json"

# Dataset Paths (Direct integration with the project datasets)
DATASET_ROOT = BASE_DIR / "Dataset"
DATASET_1_DIR = DATASET_ROOT / "Dataset 1"
DATASET_1_CSV = DATASET_1_DIR / "Resume" / "Resume.csv"
DATASET_1_PDF_DIR = DATASET_1_DIR / "data" / "data"

DATASET_2_DIR = DATASET_ROOT / "Dataset 2"
DATASET_2_CSV = DATASET_2_DIR / "job_descriptions.csv"

# Default Scoring Weights (Must sum to 100%)
DEFAULT_WEIGHTS = {
    "required_skills": 0.40,
    "similarity": 0.25,
    "preferred_skills": 0.15,
    "experience": 0.10,
    "education": 0.05,
    "keyword": 0.05,
}

# Recommendation Thresholds
THRESHOLD_STRONG_MATCH = 80.0
THRESHOLD_GOOD_MATCH = 65.0
THRESHOLD_PARTIAL_MATCH = 45.0

# Supported Upload File Extensions
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]
MAX_FILE_SIZE_MB = 15

# UI Theme Palette
THEME = {
    "primary": "#0284c7",       # Ocean Sky
    "primary_dark": "#0369a1",
    "primary_light": "#e0f2fe",
    "secondary": "#0f172a",     # Navy Slate
    "accent": "#06b6d4",        # Cyan
    "success": "#10b981",       # Emerald Green
    "warning": "#f59e0b",       # Amber
    "danger": "#ef4444",        # Rose Red
    "background": "#f8fafc",    # Slate 50
    "card_bg": "#ffffff",
    "text_main": "#0f172a",
    "text_muted": "#64748b",
    "border": "#e2e8f0"
}
