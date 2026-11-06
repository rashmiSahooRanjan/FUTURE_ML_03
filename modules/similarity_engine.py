"""
Similarity Engine for TalentRank AI
Computes TF-IDF representations and Cosine Similarity between resumes and job descriptions.
"""

from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityEngine:
    def __init__(self):
        # Uses unigrams and bigrams, sublinear tf scaling for natural term frequency normalization
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words='english',
            max_features=5000
        )

    def compute_similarity(self, resume_text: str, job_description_text: str) -> float:
        """
        Calculates cosine similarity between a single resume and job description.
        Returns a score between 0.0 and 100.0.
        """
        if not resume_text.strip() or not job_description_text.strip():
            return 0.0

        try:
            tfidf_matrix = self.vectorizer.fit_transform([job_description_text, resume_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Convert to percentage and cap between 0 and 100
            score = float(np.clip(similarity * 100.0, 0.0, 100.0))
            return round(score, 2)
        except Exception:
            return 0.0

    def compute_batch_similarity(self, resume_texts: List[str], job_description_text: str) -> List[float]:
        """
        Computes cosine similarities for a batch of resumes against a single job description.
        Returns a list of percentage scores.
        """
        if not job_description_text.strip() or not resume_texts:
            return [0.0] * len(resume_texts)

        corpus = [job_description_text] + resume_texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            scores = (sim_matrix[0] * 100.0).clip(0.0, 100.0)
            return [round(float(s), 2) for s in scores]
        except Exception:
            return [self.compute_similarity(r, job_description_text) for r in resume_texts]


similarity_engine = SimilarityEngine()

