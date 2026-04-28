"""
ai_detector.py
Heuristic-based AI-generated text detector.
No external API needed. Uses statistical signals known to differ
between human and LLM-generated text.

Signals used:
  1. Perplexity proxy  — LLMs produce very uniform sentence lengths
  2. Burstiness        — humans vary sentence length more (high std dev)
  3. Vocabulary richness — LLMs reuse formal vocabulary heavily
  4. Filler phrases    — common LLM phrases ("it is important to note", etc.)
  5. Punctuation ratio — LLMs use fewer contractions, more formal punctuation
  6. Average word length — LLMs tend toward longer, formal words
  7. Transition density — LLMs overuse transition words

Score: 0.0 (definitely human) → 1.0 (likely AI)
"""

import re
import math
from typing import Dict, Any


# Common LLM filler / boilerplate phrases
_AI_PHRASES = [
    "it is important to note",
    "it is worth noting",
    "in conclusion",
    "in summary",
    "furthermore",
    "moreover",
    "it should be noted",
    "as mentioned above",
    "as previously stated",
    "in the context of",
    "with respect to",
    "it can be seen that",
    "this demonstrates that",
    "plays a crucial role",
    "plays an important role",
    "it is essential to",
    "one must consider",
    "a comprehensive understanding",
    "delve into",
    "in today's world",
    "in the modern era",
    "needless to say",
    "it goes without saying",
    "at the end of the day",
    "in light of the above",
    "to summarize",
    "to conclude",
    "overall",
    "thus",
    "hence",
    "therefore",
    "consequently",
]

_TRANSITION_WORDS = {
    "however", "therefore", "furthermore", "moreover", "additionally",
    "consequently", "nevertheless", "nonetheless", "subsequently",
    "accordingly", "hence", "thus", "thereby", "whereas", "whereby",
}


def _sentences(text: str):
    return [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 5]


def _words(text: str):
    return re.findall(r'\b[a-zA-Z]+\b', text.lower())


def _burstiness_score(text: str) -> float:
    """Low burstiness (uniform sentence length) → more AI-like."""
    sents = _sentences(text)
    if len(sents) < 3:
        return 0.5
    lengths = [len(s.split()) for s in sents]
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    std = math.sqrt(variance)
    cv = std / mean if mean > 0 else 0  # coefficient of variation
    # Low CV → uniform → AI-like → high AI score
    ai_score = max(0.0, 1.0 - min(cv, 1.0))
    return round(ai_score, 3)


def _filler_phrase_score(text: str) -> float:
    """More filler phrases → more AI-like."""
    text_lower = text.lower()
    hits = sum(1 for phrase in _AI_PHRASES if phrase in text_lower)
    # Normalize: 3+ hits = very likely AI
    return round(min(hits / 3.0, 1.0), 3)


def _vocabulary_richness_score(text: str) -> float:
    """Low type-token ratio → repetitive → more AI-like."""
    words = _words(text)
    if len(words) < 10:
        return 0.5
    ttr = len(set(words)) / len(words)
    # Low TTR → AI-like
    ai_score = max(0.0, 1.0 - ttr)
    return round(ai_score, 3)


def _avg_word_length_score(text: str) -> float:
    """Longer average word length → more formal → more AI-like."""
    words = _words(text)
    if not words:
        return 0.5
    avg = sum(len(w) for w in words) / len(words)
    # Human avg ~4.5, AI avg ~5.5+
    ai_score = min(max((avg - 4.0) / 3.0, 0.0), 1.0)
    return round(ai_score, 3)


def _transition_density_score(text: str) -> float:
    """High transition word density → more AI-like."""
    words = _words(text)
    if not words:
        return 0.0
    count = sum(1 for w in words if w in _TRANSITION_WORDS)
    density = count / len(words)
    # Normalize: >5% transition words = very AI-like
    return round(min(density / 0.05, 1.0), 3)


def _contraction_score(text: str) -> float:
    """Fewer contractions → more formal → more AI-like."""
    contractions = len(re.findall(r"\b\w+'\w+\b", text))
    words = _words(text)
    if not words:
        return 0.5
    ratio = contractions / len(words)
    # Human text has ~2-5% contractions, AI has near 0
    ai_score = max(0.0, 1.0 - ratio / 0.03)
    return round(min(ai_score, 1.0), 3)


def detect_ai(text: str) -> Dict[str, Any]:
    """
    Run all heuristics and return a composite AI probability score.

    Returns:
        {
          "ai_score": float (0-1),
          "ai_probability_pct": float (0-100),
          "verdict": str,
          "signals": dict of individual scores
        }
    """
    if len(text.strip()) < 30:
        return {
            "ai_score": 0.0,
            "ai_probability_pct": 0.0,
            "verdict": "Too short to analyze",
            "signals": {},
        }

    signals = {
        "burstiness":         _burstiness_score(text),
        "filler_phrases":     _filler_phrase_score(text),
        "vocabulary_richness":_vocabulary_richness_score(text),
        "avg_word_length":    _avg_word_length_score(text),
        "transition_density": _transition_density_score(text),
        "formality":          _contraction_score(text),
    }

    # Weighted composite
    weights = {
        "burstiness":          0.20,
        "filler_phrases":      0.25,
        "vocabulary_richness": 0.15,
        "avg_word_length":     0.15,
        "transition_density":  0.15,
        "formality":           0.10,
    }

    ai_score = sum(signals[k] * weights[k] for k in weights)
    ai_score = round(min(max(ai_score, 0.0), 1.0), 3)
    pct = round(ai_score * 100, 1)

    if pct >= 75:
        verdict = "Likely AI-generated"
    elif pct >= 50:
        verdict = "Possibly AI-assisted"
    elif pct >= 25:
        verdict = "Likely Human-written"
    else:
        verdict = "Human-written"

    return {
        "ai_score": ai_score,
        "ai_probability_pct": pct,
        "verdict": verdict,
        "signals": signals,
    }
