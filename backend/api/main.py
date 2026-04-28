"""
FastAPI backend — Automated Answer Evaluation System
Endpoints:
  POST /evaluate          — single answer (JSON)
  POST /evaluate-batch    — multiple answers (JSON)
  POST /evaluate-pdf      — PDF upload, returns JSON report
  POST /evaluate-pdf/report — PDF upload, returns PDF report
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Optional
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.src.evaluator import evaluate as run_evaluate
from backend.src.pdf_parser import extract_text_from_pdf, parse_qa_pairs
from backend.src.ai_detector import detect_ai
from backend.src.report_generator import generate_report
from backend.src.embedding import _load as preload_model

preload_model()

app = FastAPI(
    title="Answer Evaluation API",
    description="Transformer-based semantic similarity scoring for descriptive answers.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    question: str = Field(default="")
    model_answer: str = Field(...)
    student_answer: str = Field(...)
    model_name: Optional[str] = Field(default="minilm")
    max_score: Optional[float] = Field(default=10.0)


class BatchItem(BaseModel):
    model_config = {"protected_namespaces": ()}
    question: str = Field(default="")
    model_answer: str = Field(...)
    student_answer: str = Field(...)
    model_name: Optional[str] = Field(default="minilm")
    max_score: Optional[float] = Field(default=10.0)


class BatchRequest(BaseModel):
    items: List[BatchItem]
    student_name: Optional[str] = Field(default="Student")


class FeedbackSchema(BaseModel):
    strengths: List[str]
    missing: List[str]
    improvements: List[str]


class SentenceMatch(BaseModel):
    student_sentence: str
    closest_model_sentence: str
    similarity: float
    classification: str


class AIDetection(BaseModel):
    ai_score: float
    ai_probability_pct: float
    verdict: str
    signals: dict


class EvaluateResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    question: str
    score: float
    max_score: float
    score_label: str
    similarity: float
    keyword_coverage: float
    feedback: FeedbackSchema
    sentence_analysis: List[SentenceMatch]
    model_keywords: List[str]
    summary: str
    ai_detection: AIDetection


class BatchResponse(BaseModel):
    student_name: str
    total_questions: int
    average_score_pct: float
    average_ai_probability_pct: float
    results: List[EvaluateResponse]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_response(result: dict, student_answer: str, question: str) -> EvaluateResponse:
    ai = detect_ai(student_answer)
    return EvaluateResponse(
        question=question,
        score=result["score"],
        max_score=result["max_score"],
        score_label=result["score_label"],
        similarity=result["semantic_similarity_pct"],
        keyword_coverage=result["keyword_coverage_pct"],
        feedback=FeedbackSchema(
            strengths=result["strengths"],
            missing=result["missing_concepts"],
            improvements=result["improvements"],
        ),
        sentence_analysis=[SentenceMatch(**s) for s in result["sentence_analysis"]],
        model_keywords=result.get("model_keywords", []),
        summary=result["summary"],
        ai_detection=AIDetection(**ai),
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate_single(req: EvaluateRequest):
    if not req.model_answer.strip() or not req.student_answer.strip():
        raise HTTPException(status_code=422, detail="model_answer and student_answer are required.")
    result = run_evaluate(
        question=req.question,
        model_answer=req.model_answer,
        student_answer=req.student_answer,
        model_name=req.model_name or "minilm",
        max_score=req.max_score or 10.0,
    )
    return _build_response(result, req.student_answer, req.question)


@app.post("/evaluate-batch", response_model=BatchResponse)
def evaluate_batch(req: BatchRequest):
    if not req.items:
        raise HTTPException(status_code=422, detail="No items provided.")
    results = []
    for item in req.items:
        result = run_evaluate(
            question=item.question,
            model_answer=item.model_answer,
            student_answer=item.student_answer,
            model_name=item.model_name or "minilm",
            max_score=item.max_score or 10.0,
        )
        results.append(_build_response(result, item.student_answer, item.question))

    avg_score = sum(r.score / r.max_score * 100 for r in results) / len(results)
    avg_ai    = sum(r.ai_detection.ai_probability_pct for r in results) / len(results)

    return BatchResponse(
        student_name=req.student_name or "Student",
        total_questions=len(results),
        average_score_pct=round(avg_score, 1),
        average_ai_probability_pct=round(avg_ai, 1),
        results=results,
    )


@app.post("/evaluate-pdf")
async def evaluate_pdf(
    model_pdf: UploadFile = File(..., description="PDF with model answers"),
    student_pdf: UploadFile = File(..., description="PDF with student answers"),
    student_name: str = Form(default="Student"),
    max_score: float = Form(default=10.0),
):
    """Upload two PDFs, get JSON evaluation results."""
    model_bytes   = await model_pdf.read()
    student_bytes = await student_pdf.read()

    model_text   = extract_text_from_pdf(model_bytes)
    student_text = extract_text_from_pdf(student_bytes)

    model_pairs   = parse_qa_pairs(model_text)
    student_pairs = parse_qa_pairs(student_text)

    if not model_pairs:
        raise HTTPException(status_code=422, detail="Could not parse Q&A pairs from model PDF.")
    if not student_pairs:
        raise HTTPException(status_code=422, detail="Could not parse Q&A pairs from student PDF.")

    # Match by index
    n = min(len(model_pairs), len(student_pairs))
    results = []
    for i in range(n):
        mp = model_pairs[i]
        sp = student_pairs[i]
        question = mp.get("question") or sp.get("question") or f"Question {i+1}"
        result = run_evaluate(
            question=question,
            model_answer=mp["answer"],
            student_answer=sp["answer"],
            max_score=max_score,
        )
        results.append(_build_response(result, sp["answer"], question))

    avg_score = sum(r.score / r.max_score * 100 for r in results) / len(results) if results else 0
    avg_ai    = sum(r.ai_detection.ai_probability_pct for r in results) / len(results) if results else 0

    return {
        "student_name": student_name,
        "total_questions": len(results),
        "average_score_pct": round(avg_score, 1),
        "average_ai_probability_pct": round(avg_ai, 1),
        "results": [r.model_dump() for r in results],
    }


@app.post("/evaluate-pdf/report")
async def evaluate_pdf_report(
    model_pdf: UploadFile = File(..., description="PDF with model answers"),
    student_pdf: UploadFile = File(..., description="PDF with student answers"),
    student_name: str = Form(default="Student"),
    max_score: float = Form(default=10.0),
):
    """Upload two PDFs, get a PDF evaluation report back."""
    model_bytes   = await model_pdf.read()
    student_bytes = await student_pdf.read()

    model_text   = extract_text_from_pdf(model_bytes)
    student_text = extract_text_from_pdf(student_bytes)

    model_pairs   = parse_qa_pairs(model_text)
    student_pairs = parse_qa_pairs(student_text)

    if not model_pairs:
        raise HTTPException(status_code=422, detail="Could not parse Q&A pairs from model PDF.")
    if not student_pairs:
        raise HTTPException(status_code=422, detail="Could not parse Q&A pairs from student PDF.")

    n = min(len(model_pairs), len(student_pairs))
    results = []
    for i in range(n):
        mp = model_pairs[i]
        sp = student_pairs[i]
        question = mp.get("question") or sp.get("question") or f"Question {i+1}"
        result = run_evaluate(
            question=question,
            model_answer=mp["answer"],
            student_answer=sp["answer"],
            max_score=max_score,
        )
        resp = _build_response(result, sp["answer"], question)
        results.append(resp.model_dump())

    pdf_bytes = generate_report(results, student_name=student_name)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="evaluation_report_{student_name}.pdf"'},
    )
