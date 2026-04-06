"""
embedding.py
Transformer-based embedding generation.
Uses TF-IDF based sentence-transformers compatible approach for low memory environments.
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

# paraphrase-MiniLM-L3-v2 is only ~60MB RAM vs ~400MB for all-MiniLM-L6-v2
MODEL_ALIASES = {
    "minilm": "paraphrase-MiniLM-L3-v2",
    "bert":   "paraphrase-MiniLM-L3-v2",
    "roberta":"paraphrase-MiniLM-L3-v2",
}

_model_cache: dict = {}


def load_model(model_name: str = "minilm") -> SentenceTransformer:
    resolved = MODEL_ALIASES.get(model_name, "paraphrase-MiniLM-L3-v2")
    if resolved not in _model_cache:
        _model_cache[resolved] = SentenceTransformer(resolved)
    return _model_cache[resolved]


def get_embedding(text: Union[str, List[str]], model_name: str = "minilm") -> np.ndarray:
    model = load_model(model_name)
    return model.encode(text, convert_to_numpy=True, show_progress_bar=False)
