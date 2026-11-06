"""
Skill Extraction Engine for TalentRank AI
Uses boundary-aware regex matching, alias resolution, multi-word matching,
and configurable hierarchical skill taxonomy. Prevents false positive substring matches.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any
from config import SKILLS_FILE

class SkillExtractor:
    def __init__(self, dictionary_path: Path = SKILLS_FILE):
        self.dictionary_path = dictionary_path
        self.categories: Dict[str, List[str]] = {}
        self.aliases: Dict[str, str] = {}
        self.canonical_skills: Set[str] = set()
        self.skill_to_category: Dict[str, str] = {}
        self.load_dictionary()

    def load_dictionary(self):
        """Loads or reloads the skill taxonomy and alias mappings."""
        if not self.dictionary_path.exists():
            return
        with open(self.dictionary_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.categories = data.get("categories", {})
        self.aliases = {k.lower(): v for k, v in data.get("aliases", {}).items()}

        self.canonical_skills.clear()
        self.skill_to_category.clear()

        for category, skills in self.categories.items():
            for skill in skills:
                self.canonical_skills.add(skill)
                self.skill_to_category[skill.lower()] = category

    def _build_regex(self, term: str) -> re.Pattern:
        """
        Builds a regex pattern with strict word boundaries or symbol handling.
        Handles tricky cases like C++, C#, .NET, Node.js, C, R.
        """
        term_clean = term.strip()

        if term_clean.lower() == 'c':
            # Match 'C' or 'C programming' or 'C language', not 'C++' or 'C#' or within words
            return re.compile(r'(?:\bC\b|\bc\s+programming\b|\bc\s+language\b)(?!\+|\#)', re.IGNORECASE)
        elif term_clean.lower() == 'r':
            return re.compile(r'(?:\bR\b|\br\s+programming\b|\br\s+language\b)', re.IGNORECASE)
        elif term_clean.lower() == 'c++':
            return re.compile(r'(?:\bC\+\+|\bc\s*\+\+)', re.IGNORECASE)
        elif term_clean.lower() == 'c#':
            return re.compile(r'(?:\bC\#|\bc\s*\#)', re.IGNORECASE)
        elif term_clean.lower() == '.net':
            return re.compile(r'(?:\.net|\bdotnet\b)', re.IGNORECASE)
        elif term_clean.lower() == 'node.js':
            return re.compile(r'(?:\bnode\.js\b|\bnodejs\b|\bnode\s+js\b)', re.IGNORECASE)
        elif term_clean.lower() == 'vue.js':
            return re.compile(r'(?:\bvue\.js\b|\bvuejs\b|\bvue\s+js\b)', re.IGNORECASE)
        elif term_clean.lower() == 'next.js':
            return re.compile(r'(?:\bnext\.js\b|\bnextjs\b|\bnext\s+js\b)', re.IGNORECASE)
        else:
            # Multi-word or standard single word
            escaped = re.escape(term_clean)
            return re.compile(rf'\b{escaped}\b', re.IGNORECASE)

    def extract_skills(self, text: str) -> List[str]:
        """
        Extracts unique canonical skills from input text.
        Returns deduplicated sorted list of canonical skill names.
        """
        if not text:
            return []

        matched_skills: Set[str] = set()

        # 1. Check for Alias matches
        for alias, canonical in self.aliases.items():
            pattern = self._build_regex(alias)
            if pattern.search(text):
                matched_skills.add(canonical)

        # 2. Check for Canonical Skill matches (sort by length descending to match multi-words first)
        sorted_canonical = sorted(list(self.canonical_skills), key=lambda x: len(x), reverse=True)
        for skill in sorted_canonical:
            if skill in matched_skills:
                continue
            pattern = self._build_regex(skill)
            if pattern.search(text):
                matched_skills.add(skill)

        return sorted(list(matched_skills))

    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Organizes a list of skills into taxonomy categories.
        """
        categorized: Dict[str, List[str]] = {cat: [] for cat in self.categories.keys()}
        categorized["Other Technical"] = []

        for skill in skills:
            cat = self.skill_to_category.get(skill.lower())
            if cat and cat in categorized:
                categorized[cat].append(skill)
            else:
                categorized["Other Technical"].append(skill)

        # Remove empty categories for clean presentation
        return {k: v for k, v in categorized.items() if v}


skill_extractor = SkillExtractor()

