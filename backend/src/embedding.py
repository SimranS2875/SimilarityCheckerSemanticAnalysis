"""
embedding.py - minimal memory footprint for free tier deployment.
Uses TF-IDF cosine similarity as fallback when torch is unavailable/OOM.

TF-IDF fallback note:
  Cosine similarity requires both vectors to share the same vocabulary/dimension.
  When called with a single string, we cannot guarantee compatible dimensions
  across separate calls. Use get_embeddings_pair() to embed two texts together,
  or pass a list of all texts at once so they share a single fitted vectorizer.
"""

from typing import List, Union, Tuple
import numpy as np

# Try loading sentence transformer, fall back to TF-IDF if OOM
_model = None
_use_tfidf = False


def _load():
    global _model, _use_tfidf
    if _model is not None:
        return
    # Tell transformers/huggingface to use PyTorch only — avoids Keras 3 conflict
    import os
    os.environ.setdefault("USE_TF", "0")
    os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        _use_tfidf = False
        print("Loaded SentenceTransformer model OK")
    except Exception as e:
        print(f"SentenceTransformer failed ({e}), falling back to TF-IDF")
        _use_tfidf = True


def get_embedding(text: Union[str, List[str]], model_name: str = "minilm") -> np.ndarray:
    """
    Embed one or more texts.

    WARNING (TF-IDF fallback): If called with a single string, each call fits
    its own vocabulary. Use get_embeddings_pair() when you need two embeddings
    that are comparable (same vector space).
    """
    _load()
    texts = [text] if isinstance(text, str) else text
    if _use_tfidf:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer()
        matrix = vec.fit_transform(texts).toarray()
        return matrix[0] if isinstance(text, str) else matrix
    else:
        result = _model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return result[0] if isinstance(text, str) else result


def get_embeddings_pair(text_a: str, text_b: str, model_name: str = "minilm") -> Tuple[np.ndarray, np.ndarray]:
    """
    Embed two texts in the same vector space — safe for cosine similarity.

    In TF-IDF fallback mode, both texts are fitted together so they share
    the same vocabulary and produce compatible-dimension vectors.
    In transformer mode, this is equivalent to calling get_embedding twice.
    """
    _load()
    if _use_tfidf:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vec = TfidfVectorizer()
        matrix = vec.fit_transform([text_a, text_b]).toarray()
        return matrix[0], matrix[1]
    else:
        results = _model.encode([text_a, text_b], convert_to_numpy=True, show_progress_bar=False)
        return results[0], results[1]
