"""
NLP Text Preprocessing Module for TalentRank AI
Provides clean, reliable text preprocessing while strictly preserving
technical terminology, abbreviations, and programming symbols (e.g. C++, C#, .NET, CI/CD).
"""

import re
import string
from typing import List, Set
import nltk

# Ensure NLTK resources are available with fallbacks
try:
    from nltk.corpus import stopwords
    _STOPWORDS = set(stopwords.words('english'))
except Exception:
    _STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
        "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
        "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
        "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
        "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more",
        "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
        "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
        "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's",
        "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
        "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
        "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
        "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom",
        "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
        "your", "yours", "yourself", "yourselves"
    }

try:
    from nltk.stem import WordNetLemmatizer
    _LEMMATIZER = WordNetLemmatizer()
except Exception:
    _LEMMATIZER = None


class TextPreprocessor:
    def __init__(self):
        self.stopwords = _STOPWORDS
        self.lemmatizer = _LEMMATIZER

        # Essential technical keywords/abbreviations to protect from stopword removal or truncation
        self.protected_terms = {
            "c", "r", "ai", "ml", "dl", "cv", "js", "ts", "c++", "c#", ".net", "ci/cd", "rest", "api", "sql"
        }

    def clean_text(self, text: str, remove_stop_words: bool = True, lemmatize: bool = True) -> str:
        """
        Cleans and normalizes text for feature extraction and similarity scoring.
        Preserves technical symbols like ++, #, /, dots in tech names.
        """
        if not text or not isinstance(text, str):
            return ""

        # 1. Strip HTML tags
        clean = re.sub(r'<[^>]+>', ' ', text)

        # 2. Convert to lowercase
        clean = clean.lower()

        # 3. Protect specific symbols: C++, C#, .NET, CI/CD, Node.js
        clean = clean.replace("c++", "cpp_tech")
        clean = clean.replace("c#", "csharp_tech")
        clean = clean.replace(".net", "dotnet_tech")
        clean = clean.replace("ci/cd", "cicd_tech")
        clean = clean.replace("node.js", "nodejs_tech")
        clean = clean.replace("vue.js", "vuejs_tech")
        clean = clean.replace("next.js", "nextjs_tech")

        # 4. Remove unwanted special characters, keep alphanumeric, spaces, and hyphens/underscores
        clean = re.sub(r'[^a-z0-9\s_-]', ' ', clean)

        # 5. Tokenize
        tokens = clean.split()

        # 6. Stopwords & Lemmatization
        processed_tokens = []
        seen = set()

        for token in tokens:
            # Restore protected tokens
            if token == "cpp_tech":
                token = "c++"
            elif token == "csharp_tech":
                token = "c#"
            elif token == "dotnet_tech":
                token = ".net"
            elif token == "cicd_tech":
                token = "ci/cd"
            elif token == "nodejs_tech":
                token = "node.js"
            elif token == "vuejs_tech":
                token = "vue.js"
            elif token == "nextjs_tech":
                token = "next.js"

            # Filter stopwords unless protected
            if remove_stop_words and token in self.stopwords and token not in self.protected_terms:
                continue

            # Lemmatize
            if lemmatize and self.lemmatizer and len(token) > 2 and token not in self.protected_terms:
                try:
                    token = self.lemmatizer.lemmatize(token)
                except Exception:
                    pass

            if token and len(token) > 0:
                processed_tokens.append(token)

        return " ".join(processed_tokens)

    def tokenize(self, text: str) -> List[str]:
        """Returns clean list of tokens."""
        cleaned = self.clean_text(text)
        return cleaned.split()


preprocessor = TextPreprocessor()
