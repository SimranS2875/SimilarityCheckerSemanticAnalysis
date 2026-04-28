"""
similarity.py
Cosine similarity computation between embeddings.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
from typing import List, Tuple


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two 1-D vectors."""
    a = vec_a.reshape(1, -1)
    b = vec_b.reshape(1, -1)
    return float(sk_cosine(a, b)[0][0])


def sentence_level_similarity(
    student_sentences: List[str],
    model_sentences: List[str],
    model_name: str = "minilm",
) -> List[Tuple[str, str, float]]:
    """
    Match each student sentence to the closest model sentence.

    Returns:
        List of (student_sentence, best_model_sentence, similarity_score)
    """
    from backend.src.embedding import get_embedding

    if not student_sentences or not model_sentences:
        return []

    # Embed all sentences together so they share the same vector space.
    # This is critical for the TF-IDF fallback where separate fit() calls
    # produce incompatible vocabulary dimensions.
    all_sentences = student_sentences + model_sentences
    all_embs = get_embedding(all_sentences, model_name)

    student_embs = all_embs[:len(student_sentences)]
    model_embs   = all_embs[len(student_sentences):]

    results = []
    for i, s_emb in enumerate(student_embs):
        sims = [cosine_similarity(s_emb, m_emb) for m_emb in model_embs]
        best_idx = int(np.argmax(sims))
        results.append((
            student_sentences[i],
            model_sentences[best_idx],
            round(sims[best_idx], 4),
        ))
    return results
