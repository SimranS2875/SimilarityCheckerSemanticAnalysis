"""
evaluator.py
Main evaluation pipeline orchestrator.
"""

from typing import Dict, Any

from backend.src.preprocessing import preprocess, split_into_sentences
from backend.src.embedding import get_embedding
from backend.src.similarity import cosine_similarity, sentence_level_similarity
from backend.src.scoring import keyword_coverage, compute_hybrid_score
from backend.src.feedback import generate_feedback


def evaluate(
    question: str,
    model_answer: str,
    student_answer: str,
    model_name: str = "minilm",
    max_score: float = 10.0,
) -> Dict[str, Any]:
    """Full evaluation pipeline."""
    clean_model = preprocess(model_answer)
    clean_student = preprocess(student_answer)

    model_sentences = split_into_sentences(clean_model)
    student_sentences = split_into_sentences(clean_student)

    model_emb = get_embedding(clean_model, model_name)
    student_emb = get_embedding(clean_student, model_name)

    sem_sim = cosine_similarity(model_emb, student_emb)
    kw_cov, model_kws, missing_kws = keyword_coverage(clean_model, clean_student)
    final_score = compute_hybrid_score(sem_sim, kw_cov, max_score)
    sentence_matches = sentence_level_similarity(student_sentences, model_sentences, model_name)

    feedback = generate_feedback(
        score=final_score,
        max_score=max_score,
        semantic_sim=sem_sim,
        kw_coverage=kw_cov,
        missing_keywords=missing_kws,
        sentence_matches=sentence_matches,
    )

    feedback["question"] = question
    feedback["model_keywords"] = model_kws
    return feedback
