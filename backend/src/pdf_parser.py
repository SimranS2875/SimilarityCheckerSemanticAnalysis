"""
pdf_parser.py
Extract Q&A pairs from uploaded PDFs.

Expected PDF format (flexible):
  Q1: What is machine learning?
  A1: Machine learning is...

  Q2: Explain photosynthesis.
  A2: Photosynthesis is...

Also supports:
  Question 1: ...
  Answer 1: ...

  1. What is ...
  Answer: ...
"""

import re
from typing import List, Dict
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF given its raw bytes."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_qa_pairs(text: str) -> List[Dict[str, str]]:
    """
    Parse Q&A pairs from extracted PDF text.
    Returns list of {"question": ..., "answer": ...}
    """
    pairs = []

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Try pattern: Q1:/A1: or Question 1:/Answer 1:
    pattern = re.compile(
        r'(?:Q(?:uestion)?\s*(\d+)\s*[:\.\)]\s*)(.*?)(?=(?:A(?:nswer)?\s*\1\s*[:\.\)])|$)',
        re.IGNORECASE | re.DOTALL
    )
    answer_pattern = re.compile(
        r'A(?:nswer)?\s*(\d+)\s*[:\.\)]\s*(.*?)(?=(?:Q(?:uestion)?\s*\d+\s*[:\.\)])|A(?:nswer)?\s*\d+\s*[:\.\)]|$)',
        re.IGNORECASE | re.DOTALL
    )

    questions = {m.group(1): m.group(2).strip() for m in pattern.finditer(text)}
    answers   = {m.group(1): m.group(2).strip() for m in answer_pattern.finditer(text)}

    if questions and answers:
        for num in sorted(questions.keys(), key=lambda x: int(x)):
            q = questions.get(num, "").strip()
            a = answers.get(num, "").strip()
            if q and a:
                pairs.append({"question": q, "answer": a})
        if pairs:
            return pairs

    # Fallback: split by numbered lines "1." or "1)"
    blocks = re.split(r'\n\s*\n', text.strip())
    current_q = None
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        q_match = re.match(r'^(?:Q(?:uestion)?\s*\d*\s*[:\.\)]?\s*)(.*)', block, re.IGNORECASE)
        a_match = re.match(r'^(?:A(?:nswer)?\s*\d*\s*[:\.\)]?\s*)(.*)', block, re.IGNORECASE | re.DOTALL)
        if q_match:
            current_q = q_match.group(1).strip()
        elif a_match and current_q:
            pairs.append({"question": current_q, "answer": a_match.group(1).strip()})
            current_q = None

    if pairs:
        return pairs

    # Last resort: treat alternating paragraphs as Q/A
    blocks = [b.strip() for b in re.split(r'\n\s*\n', text.strip()) if b.strip()]
    for i in range(0, len(blocks) - 1, 2):
        pairs.append({"question": blocks[i], "answer": blocks[i + 1]})

    return pairs
