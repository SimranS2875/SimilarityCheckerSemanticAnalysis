"""
test_pdf_pipeline.py
End-to-end test for the PDF evaluation pipeline.

Tests:
  1. PDF generation (create test PDFs in memory)
  2. pdf_parser: extract_text_from_pdf + parse_qa_pairs
  3. POST /evaluate-pdf  → JSON response validation
  4. POST /evaluate-pdf/report → PDF bytes returned
  5. Edge cases: mismatched Q count, malformed PDF bytes

Run:
  python tests/test_pdf_pipeline.py
  (backend must be running on localhost:8000)
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import io
import json
import requests
from fpdf import FPDF

BASE_URL = "http://localhost:8000"

# ── Helpers ────────────────────────────────────────────────────────────────────

def make_pdf(qa_pairs: list[dict]) -> bytes:
    """Create a minimal PDF with Q/A pairs in the expected format."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for i, pair in enumerate(qa_pairs, start=1):
        if pair.get("question"):
            pdf.multi_cell(0, 8, f"Q{i}: {pair['question']}")
            pdf.ln(1)
        pdf.multi_cell(0, 8, f"A{i}: {pair['answer']}")
        pdf.ln(4)
    return bytes(pdf.output())


def section(title: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


def ok(msg: str):   print(f"  ✓  {msg}")
def fail(msg: str): print(f"  ✗  {msg}")


# ── Unit tests: pdf_parser (no server needed) ──────────────────────────────────

def test_parser_unit():
    section("UNIT — pdf_parser: extract_text + parse_qa_pairs")
    from backend.src.pdf_parser import extract_text_from_pdf, parse_qa_pairs

    qa_pairs = [
        {"question": "What is machine learning?",
         "answer": "Machine learning is a subset of AI that enables systems to learn from data."},
        {"question": "Explain photosynthesis.",
         "answer": "Photosynthesis is the process by which plants convert sunlight into glucose."},
    ]
    pdf_bytes = make_pdf(qa_pairs)

    # 1. extract_text_from_pdf
    text = extract_text_from_pdf(pdf_bytes)
    assert isinstance(text, str) and len(text) > 10, "Extracted text is empty"
    ok(f"extract_text_from_pdf returned {len(text)} chars")

    # 2. parse_qa_pairs
    parsed = parse_qa_pairs(text)
    assert len(parsed) == 2, f"Expected 2 pairs, got {len(parsed)}: {parsed}"
    ok(f"parse_qa_pairs returned {len(parsed)} Q&A pairs")

    for i, p in enumerate(parsed):
        assert "question" in p and "answer" in p, f"Pair {i} missing keys: {p}"
        assert len(p["answer"]) > 5, f"Pair {i} answer too short: {p['answer']!r}"
        ok(f"  Pair {i+1} — Q: {p['question'][:50]!r}")
        ok(f"  Pair {i+1} — A: {p['answer'][:60]!r}")

    # 3. Single Q&A
    single_pdf = make_pdf([{"question": "What is DNA?",
                             "answer": "DNA carries genetic information in living organisms."}])
    single_text = extract_text_from_pdf(single_pdf)
    single_parsed = parse_qa_pairs(single_text)
    assert len(single_parsed) >= 1, f"Expected 1 pair, got {len(single_parsed)}"
    ok(f"Single Q&A parsed correctly")

    # 4. Answer-only PDF (no question field)
    answer_only = make_pdf([{"question": "", "answer": "Machine learning uses data to train models."},
                             {"question": "", "answer": "Photosynthesis converts light to glucose."}])
    ao_text = extract_text_from_pdf(answer_only)
    ao_parsed = parse_qa_pairs(ao_text)
    ok(f"Answer-only PDF: got {len(ao_parsed)} pair(s) (fallback parsing)")

    print("\n  Parser unit tests PASSED")


# ── Integration tests: live API ────────────────────────────────────────────────

def check_server():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        assert r.status_code == 200
        ok("Backend is reachable at localhost:8000")
        return True
    except Exception as e:
        fail(f"Backend not reachable: {e}")
        return False


def test_evaluate_pdf_json():
    section("INTEGRATION — POST /evaluate-pdf (JSON response)")

    model_pairs = [
        {"question": "What is machine learning?",
         "answer": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed."},
        {"question": "Explain photosynthesis.",
         "answer": "Photosynthesis is the process by which green plants use sunlight to synthesize nutrients from carbon dioxide and water, releasing oxygen as a byproduct."},
    ]
    student_pairs = [
        {"question": "What is machine learning?",
         "answer": "Machine learning is a branch of AI where computers learn patterns from data and make decisions without being directly programmed for each task."},
        {"question": "Explain photosynthesis.",
         "answer": "Photosynthesis is how plants make food using sunlight and water. Oxygen is released in the process."},
    ]

    model_pdf_bytes   = make_pdf(model_pairs)
    student_pdf_bytes = make_pdf(student_pairs)

    files = {
        "model_pdf":   ("model.pdf",   model_pdf_bytes,   "application/pdf"),
        "student_pdf": ("student.pdf", student_pdf_bytes, "application/pdf"),
    }
    data = {"student_name": "Test Student", "max_score": "10"}

    r = requests.post(f"{BASE_URL}/evaluate-pdf", files=files, data=data, timeout=120)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:300]}"
    ok(f"Status: {r.status_code}")

    body = r.json()

    # Top-level fields
    assert body["student_name"] == "Test Student", f"student_name mismatch: {body['student_name']}"
    ok(f"student_name: {body['student_name']}")

    assert body["total_questions"] == 2, f"Expected 2 questions, got {body['total_questions']}"
    ok(f"total_questions: {body['total_questions']}")

    assert 0 <= body["average_score_pct"] <= 100, f"avg score out of range: {body['average_score_pct']}"
    ok(f"average_score_pct: {body['average_score_pct']}%")

    assert 0 <= body["average_ai_probability_pct"] <= 100
    ok(f"average_ai_probability_pct: {body['average_ai_probability_pct']}%")

    # Per-question results
    results = body["results"]
    assert len(results) == 2, f"Expected 2 results, got {len(results)}"

    for i, res in enumerate(results):
        ok(f"\n  --- Question {i+1} ---")
        assert 0 <= res["score"] <= res["max_score"], f"Score out of range: {res['score']}"
        ok(f"  score: {res['score']}/{res['max_score']}  ({res['score_label']})")

        assert 0 <= res["similarity"] <= 100
        ok(f"  similarity: {res['similarity']}%")

        assert 0 <= res["keyword_coverage"] <= 100
        ok(f"  keyword_coverage: {res['keyword_coverage']}%")

        assert "strengths" in res["feedback"]
        assert "missing" in res["feedback"]
        assert "improvements" in res["feedback"]
        ok(f"  feedback keys present")

        assert isinstance(res["sentence_analysis"], list)
        ok(f"  sentence_analysis: {len(res['sentence_analysis'])} entries")

        assert isinstance(res["model_keywords"], list)
        ok(f"  model_keywords: {res['model_keywords']}")

        ai = res["ai_detection"]
        assert "ai_score" in ai and "ai_probability_pct" in ai and "verdict" in ai and "signals" in ai
        ok(f"  ai_detection: {ai['verdict']} ({ai['ai_probability_pct']}%)")
        assert isinstance(ai["signals"], dict) and len(ai["signals"]) > 0
        ok(f"  ai signals: {list(ai['signals'].keys())}")

    print("\n  /evaluate-pdf JSON tests PASSED")
    return body


def test_evaluate_pdf_report():
    section("INTEGRATION — POST /evaluate-pdf/report (PDF bytes response)")

    model_pairs = [
        {"question": "What is Newton's second law?",
         "answer": "Newton's second law states that force equals mass times acceleration (F=ma). The acceleration of an object is directly proportional to the net force and inversely proportional to its mass."},
    ]
    student_pairs = [
        {"question": "What is Newton's second law?",
         "answer": "Newton's second law says F equals ma. Greater force means more acceleration."},
    ]

    files = {
        "model_pdf":   ("model.pdf",   make_pdf(model_pairs),   "application/pdf"),
        "student_pdf": ("student.pdf", make_pdf(student_pairs), "application/pdf"),
    }
    data = {"student_name": "Report Student", "max_score": "10"}

    r = requests.post(f"{BASE_URL}/evaluate-pdf/report", files=files, data=data, timeout=120)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:300]}"
    ok(f"Status: {r.status_code}")

    content_type = r.headers.get("content-type", "")
    assert "application/pdf" in content_type, f"Expected PDF content-type, got: {content_type}"
    ok(f"Content-Type: {content_type}")

    content_disp = r.headers.get("content-disposition", "")
    assert "attachment" in content_disp, f"Expected attachment header, got: {content_disp}"
    ok(f"Content-Disposition: {content_disp}")

    pdf_bytes = r.content
    assert len(pdf_bytes) > 500, f"PDF too small ({len(pdf_bytes)} bytes), likely empty"
    ok(f"PDF size: {len(pdf_bytes):,} bytes")

    # Verify it's a real PDF
    assert pdf_bytes[:4] == b"%PDF", f"Response is not a valid PDF (magic bytes: {pdf_bytes[:4]})"
    ok("PDF magic bytes valid (%PDF)")

    # Save for manual inspection
    out_path = os.path.join(os.path.dirname(__file__), "..", "results", "test_report_output.pdf")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    ok(f"Saved to: {os.path.normpath(out_path)}")

    print("\n  /evaluate-pdf/report tests PASSED")


def test_edge_cases():
    section("EDGE CASES")

    # 1. Mismatched Q count (model has 2, student has 1) — should evaluate min(2,1)=1
    model_pairs = [
        {"question": "Q1", "answer": "Answer one about machine learning and AI systems."},
        {"question": "Q2", "answer": "Answer two about photosynthesis and plant biology."},
    ]
    student_pairs = [
        {"question": "Q1", "answer": "Machine learning helps computers learn from data."},
    ]
    files = {
        "model_pdf":   ("model.pdf",   make_pdf(model_pairs),   "application/pdf"),
        "student_pdf": ("student.pdf", make_pdf(student_pairs), "application/pdf"),
    }
    r = requests.post(f"{BASE_URL}/evaluate-pdf", files={"model_pdf": ("m.pdf", make_pdf(model_pairs), "application/pdf"),
                                                          "student_pdf": ("s.pdf", make_pdf(student_pairs), "application/pdf")},
                      data={"student_name": "Edge", "max_score": "10"}, timeout=60)
    assert r.status_code == 200
    body = r.json()
    assert body["total_questions"] == 1, f"Expected 1 (min of 2,1), got {body['total_questions']}"
    ok(f"Mismatched Q count: evaluated {body['total_questions']} question(s) (min of 2 and 1)")

    # 2. Invalid (non-PDF) bytes → expect 422 or 500
    bad_bytes = b"this is not a pdf at all"
    r2 = requests.post(f"{BASE_URL}/evaluate-pdf",
                       files={"model_pdf": ("bad.pdf", bad_bytes, "application/pdf"),
                               "student_pdf": ("bad2.pdf", bad_bytes, "application/pdf")},
                       data={"student_name": "Bad", "max_score": "10"}, timeout=30)
    assert r2.status_code in (422, 500), f"Expected 422/500 for bad PDF, got {r2.status_code}"
    ok(f"Invalid PDF bytes → HTTP {r2.status_code} (expected error)")

    # 3. Empty answers in PDF → should still return a result or a clear error
    empty_pairs = [{"question": "What is AI?", "answer": "AI."}]
    r3 = requests.post(f"{BASE_URL}/evaluate-pdf",
                       files={"model_pdf":   ("m.pdf", make_pdf(empty_pairs), "application/pdf"),
                               "student_pdf": ("s.pdf", make_pdf(empty_pairs), "application/pdf")},
                       data={"student_name": "Short", "max_score": "10"}, timeout=60)
    ok(f"Very short answers → HTTP {r3.status_code}")

    print("\n  Edge case tests PASSED")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PDF PIPELINE — END-TO-END TEST SUITE")
    print("="*60)

    # Always run unit tests (no server needed)
    try:
        test_parser_unit()
    except Exception as e:
        fail(f"Parser unit test FAILED: {e}")
        import traceback; traceback.print_exc()

    # Integration tests require the server
    section("Checking backend server...")
    if not check_server():
        print("\n  ⚠  Start the backend first:")
        print("     uvicorn backend.api.main:app --reload --port 8000")
        print("\n  Skipping integration tests.\n")
        sys.exit(1)

    errors = []
    for test_fn in [test_evaluate_pdf_json, test_evaluate_pdf_report, test_edge_cases]:
        try:
            test_fn()
        except Exception as e:
            fail(f"{test_fn.__name__} FAILED: {e}")
            import traceback; traceback.print_exc()
            errors.append(test_fn.__name__)

    print("\n" + "="*60)
    if errors:
        print(f"  FAILED: {errors}")
    else:
        print("  ALL TESTS PASSED ✓")
    print("="*60 + "\n")
