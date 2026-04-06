"""
preprocessing.py
Text preprocessing utilities for answer normalization.
"""

import re
import string
from typing import List


def normalize_text(text: str) -> str:
    """Lowercase, strip extra whitespace, and remove punctuation artifacts."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using simple punctuation rules."""
    # Split on . ! ? followed by space or end
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def preprocess(text: str) -> str:
    """Full preprocessing pipeline for a single text."""
    return normalize_text(text)
