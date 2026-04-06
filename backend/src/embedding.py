"""
embedding.py - minimal memory footprint for free tier deployment.
Uses TF-IDF cosine similarity as fallback when torch is unavailable/OOM.
"""

from typing import List, Union
import numpy as np

# Try loading sentence transformer, fall back to TF-IDF if OOM
_model = None
_use_tfidf = False


def _load():
    global _model, _use_tfidf
    if _model is not None:
        return
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        _use_tfidf = False
        print("Loaded SentenceTransformer model OK")
    except Exception as e:
        print(f"SentenceTransformer failed ({e}), falling back to TF-IDF")
        from sklearn.feature_extraction.text import TfidfVectorizer
        _model = TfidfVectorizer()
        _use_tfidf = True


def get_embedding(text: Union[str, List[str]], model_name: str = "minilm") -> np.ndarray:
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
