"""
feedback.py
Structured feedback generation based on scoring and sentence analysis.
"""

from typing import List, Tuple, Dict, Any


SIMILARITY_THRESHOLDS = {
    "strong": 0.75,
    "moderate": 0.50,
    "weak": 0.30,
}


def classify_sentence(sim: float) -> str:
    """Classify a sentence match as strong / moderate / weak / irrelevant."""
    if sim >= SIMILARITY_THRESHOLDS["strong"]:
        return "strong"
    elif sim >= SIMILARITY_THRESHOLDS["moderate"]:
        return "moderate"
    elif sim >= SIMILARITY_THRESHOLDS["weak"]:
        return "weak"
    else:
        return "irrelevant"


def generate_feedback(
    score: float,
    max_score: float,
    semantic_sim: float,
    kw_coverage: float,
    missing_keywords: List[str],
    sentence_matches: List[Tuple[str, str, float]],
) -> Dict[str, Any]:
    """
    Build a structured feedback dictionary.

    Returns dict with keys: score_label, strengths, missing_concepts,
    improvements, sentence_analysis, summary
    """
    pct = score / max_score

    # ── Score label ──────────────────────────────────────────────────────────
    if pct >= 0.85:
        score_label = "Excellent"
    elif pct >= 0.70:
        score_label = "Good"
    elif pct >= 0.50:
        score_label = "Average"
    elif pct >= 0.30:
        score_label = "Below Average"
    else:
        score_label = "Poor"

    # ── Strengths ─────────────────────────────────────────────────────────────
    strengths = []
    strong_sentences = [s for s, _, sim in sentence_matches if classify_sentence(sim) == "strong"]
    if strong_sentences:
        strengths.append(f"{len(strong_sentences)} sentence(s) closely match the model answer.")
    if semantic_sim >= 0.7:
        strengths.append("Overall semantic meaning is well captured.")
    if kw_coverage >= 0.7:
        strengths.append("Good coverage of key concepts and terminology.")

    # ── Missing concepts ──────────────────────────────────────────────────────
    missing_concepts = []
    if missing_keywords:
        missing_concepts.append(f"Missing keywords: {', '.join(missing_keywords[:8])}.")
    weak_or_irrelevant = [
        s for s, _, sim in sentence_matches
        if classify_sentence(sim) in ("weak", "irrelevant")
    ]
    if weak_or_irrelevant:
        missing_concepts.append(
            f"{len(weak_or_irrelevant)} sentence(s) have low relevance to the model answer."
        )

    # ── Improvements ──────────────────────────────────────────────────────────
    improvements = []
    if semantic_sim < 0.5:
        improvements.append("Try to align your answer more closely with the core concepts.")
    if kw_coverage < 0.5:
        improvements.append("Include more domain-specific terminology from the topic.")
    if pct < 0.7:
        improvements.append("Expand your answer with more detail and examples.")
    if not improvements:
        improvements.append("Keep up the good work. Minor refinements can push the score higher.")

    # ── Sentence-level analysis ───────────────────────────────────────────────
    sentence_analysis = []
    for student_sent, model_sent, sim in sentence_matches:
        sentence_analysis.append({
            "student_sentence": student_sent,
            "closest_model_sentence": model_sent,
            "similarity": sim,
            "classification": classify_sentence(sim),
        })

    # ── Summary ───────────────────────────────────────────────────────────────
    summary = (
        f"Score: {score}/{max_score} ({score_label}). "
        f"Semantic similarity: {round(semantic_sim * 100, 1)}%. "
        f"Keyword coverage: {round(kw_coverage * 100, 1)}%."
    )

    return {
        "score": score,
        "max_score": max_score,
        "score_label": score_label,
        "semantic_similarity_pct": round(semantic_sim * 100, 1),
        "keyword_coverage_pct": round(kw_coverage * 100, 1),
        "strengths": strengths,
        "missing_concepts": missing_concepts,
        "improvements": improvements,
        "sentence_analysis": sentence_analysis,
        "summary": summary,
    }
