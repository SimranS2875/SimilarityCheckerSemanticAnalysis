"""
embedding.py
Transformer-based embedding generation.
Supports: all-MiniLM-L6-v2 (default), BERT, RoBERTa
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

# Supported model aliases
MODEL_ALIASES = {
    "minilm": "all-MiniLM-L6-v2",
    "bert": "bert-base-nli-mean-tokens",
    "roberta": "stsb-roberta-base",
}

_model_cache: dict = {}


def load_model(model_name: str = "minilm") -> SentenceTransformer:
    """Load and cache a SentenceTransformer model by alias or full name."""
    resolved = MODEL_ALIASES.get(model_name, model_name)
    if resolved not in _model_cache:
        _model_cache[resolved] = SentenceTransformer(resolved)
    return _model_cache[resolved]


def get_embedding(text: Union[str, List[str]], model_name: str = "minilm") -> np.ndarray:
    """
    Generate embedding(s) for text or list of texts.

    Args:
        text: Single string or list of strings.
        model_name: Model alias or full HuggingFace model name.

    Returns:
        numpy array of shape (embedding_dim,) or (n, embedding_dim)
    """
    model = load_model(model_name)
    embeddings = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
    return embeddings
