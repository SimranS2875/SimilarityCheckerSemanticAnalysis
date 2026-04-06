"""
evaluator.py
Main evaluation pipeline orchestrator.
"""

from typing import Dict, Any

from src.preprocessing import preprocess, split_into_sentences
from src.embedding import get_embedding
from src.similarity import cosine_similarity, sentence_level_similarity
from src.scoring import keyword_coverage, compute_hybrid_score
from src.feedback import generate_feedback


def evaluate(
    question: str,
    model_answer: str,
    student_answer: str,
    model_name: str = "minilm",
    max_score: float = 10.0,
) -> Dict[str, Any]:
    """
    Full evaluation pipeline.

    Args:
        question: The exam question (used for context, not scoring).
        model_answer: Reference/ideal answer.
        student_answer: Student's submitted answer.
        model_name: Transformer model alias ('minilm', 'bert', 'roberta').
        max_score: Maximum achievable score.

    Returns:
        Dictionary with score, feedback, and analysis details.
    """
    # 1. Preprocess
    clean_model = preprocess(model_answer)
    clean_student = preprocess(student_answer)

    # 2. Sentence splitting
    model_sentences = split_into_sentences(clean_model)
    student_sentences = split_into_sentences(clean_student)

    # 3. Embeddings
    model_emb = get_embedding(clean_model, model_name)
    student_emb = get_embedding(clean_student, model_name)

    # 4. Semantic similarity (document level)
    sem_sim = cosine_similarity(model_emb, student_emb)

    # 5. Keyword coverage
    kw_cov, model_kws, missing_kws = keyword_coverage(clean_model, clean_student)

    # 6. Hybrid score
    final_score = compute_hybrid_score(sem_sim, kw_cov, max_score)

    # 7. Sentence-level analysis
    sentence_matches = sentence_level_similarity(student_sentences, model_sentences, model_name)

    # 8. Feedback
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
