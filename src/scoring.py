"""
scoring.py
Hybrid scoring: semantic similarity + keyword coverage.
final_score = 0.7 * semantic_similarity + 0.3 * keyword_coverage
"""

import re
from typing import List, Tuple
import numpy as np


# ── Keyword extraction (lightweight, no external model needed) ──────────────

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "on", "at", "by", "for", "with", "about",
    "against", "between", "into", "through", "during", "before", "after",
    "above", "below", "from", "up", "down", "out", "off", "over", "under",
    "again", "further", "then", "once", "and", "but", "or", "nor", "so",
    "yet", "both", "either", "neither", "not", "only", "own", "same",
    "than", "too", "very", "just", "because", "as", "until", "while",
    "that", "this", "these", "those", "it", "its", "they", "them", "their",
    "what", "which", "who", "whom", "when", "where", "why", "how", "all",
    "each", "every", "both", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "same", "so", "than", "also",
}


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract important keywords by removing stopwords and short tokens."""
    tokens = re.findall(r'\b[a-z]{3,}\b', text.lower())
    keywords = [t for t in tokens if t not in _STOPWORDS]
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            unique.append(k)
    return unique[:top_n]


def keyword_coverage(model_answer: str, student_answer: str, top_n: int = 10) -> Tuple[float, List[str], List[str]]:
    """
    Compute what fraction of model keywords appear in the student answer.

    Returns:
        (coverage_ratio, model_keywords, missing_keywords)
    """
    model_kws = extract_keywords(model_answer, top_n)
    student_text = student_answer.lower()

    present = [kw for kw in model_kws if kw in student_text]
    missing = [kw for kw in model_kws if kw not in student_text]

    ratio = len(present) / len(model_kws) if model_kws else 0.0
    return round(ratio, 4), model_kws, missing


def compute_hybrid_score(
    semantic_sim: float,
    kw_coverage: float,
    max_score: float = 10.0,
    sem_weight: float = 0.7,
    kw_weight: float = 0.3,
) -> float:
    """
    Compute final hybrid score.

    final_score = (0.7 * semantic_sim + 0.3 * kw_coverage) * max_score
    """
    raw = sem_weight * semantic_sim + kw_weight * kw_coverage
    return round(raw * max_score, 2)
