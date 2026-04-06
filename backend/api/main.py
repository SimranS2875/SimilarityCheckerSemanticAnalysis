"""
FastAPI backend for Automated Answer Evaluation System.
Run from project root: uvicorn backend.api.main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import sys, os

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.src.evaluator import evaluate as run_evaluate

app = FastAPI(
    title="Answer Evaluation API",
    description="Transformer-based semantic similarity scoring for descriptive answers.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    question: str = Field(default="", description="The exam question")
    model_answer: str = Field(..., description="Reference/ideal answer")
    student_answer: str = Field(..., description="Student's submitted answer")
    model_name: Optional[str] = Field(default="minilm", description="minilm | bert | roberta")
    max_score: Optional[float] = Field(default=10.0, description="Maximum achievable score")


class FeedbackSchema(BaseModel):
    strengths: List[str]
    missing: List[str]
    improvements: List[str]


class SentenceMatch(BaseModel):
    student_sentence: str
    closest_model_sentence: str
    similarity: float
    classification: str


class EvaluateResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    score: float
    max_score: float
    score_label: str
    similarity: float          # 0–100
    keyword_coverage: float    # 0–100
    feedback: FeedbackSchema
    sentence_analysis: List[SentenceMatch]
    model_keywords: List[str]
    summary: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "message": "Answer Evaluation API is running."}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest):
    if not req.model_answer.strip() or not req.student_answer.strip():
        raise HTTPException(status_code=422, detail="model_answer and student_answer are required.")

    result = run_evaluate(
        question=req.question,
        model_answer=req.model_answer,
        student_answer=req.student_answer,
        model_name=req.model_name or "minilm",
        max_score=req.max_score or 10.0,
    )

    return EvaluateResponse(
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
        sentence_analysis=[
            SentenceMatch(**s) for s in result["sentence_analysis"]
        ],
        model_keywords=result.get("model_keywords", []),
        summary=result["summary"],
    )
