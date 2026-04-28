# EvalAI — Automated Descriptive Answer Evaluation
### Transformer-Based Semantic Similarity · FastAPI + React

A full-stack NLP system that evaluates student descriptive answers against a reference answer using transformer embeddings, hybrid scoring, AI-generated text detection, and structured feedback. Supports single answer evaluation, batch JSON evaluation, and PDF upload with downloadable PDF reports.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React + TypeScript                    │
│         (Vite · Tailwind CSS · Framer Motion)            │
│                   localhost:5173                         │
└──────────────────────┬──────────────────────────────────┘
                       │  HTTP (Axios)
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│                   localhost:8000                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              NLP Pipeline                       │    │
│  │  Preprocess → Embed → Cosine Sim → Hybrid Score │    │
│  │  Keyword Coverage → Sentence Analysis → Feedback│    │
│  │  AI Detection (heuristic, no external API)      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
project/
├── backend/
│   ├── api/
│   │   └── main.py             # FastAPI app — all endpoints
│   ├── src/
│   │   ├── preprocessing.py    # Text normalisation, sentence splitting
│   │   ├── embedding.py        # SentenceTransformer wrapper + TF-IDF fallback
│   │   ├── similarity.py       # Cosine + sentence-level similarity
│   │   ├── scoring.py          # Keyword extraction + hybrid scoring
│   │   ├── feedback.py         # Structured feedback generation
│   │   ├── evaluator.py        # Pipeline orchestrator
│   │   ├── ai_detector.py      # Heuristic AI-text detector
│   │   ├── pdf_parser.py       # PDF text extraction + Q&A parsing
│   │   └── report_generator.py # PDF report generation (fpdf2)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InputForm.tsx       # Single answer form
│   │   │   ├── PDFUploadForm.tsx   # Drag-and-drop PDF upload
│   │   │   ├── ResultCard.tsx      # Score ring, feedback, sentence analysis
│   │   │   ├── BatchResultCard.tsx # Per-question cards + PDF download
│   │   │   ├── FeedbackList.tsx    # Strengths / missing / improvements
│   │   │   └── Loader.tsx
│   │   ├── services/
│   │   │   └── api.ts          # Typed Axios wrappers
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── tailwind.config.js
├── data/
│   ├── sample_model_answers.pdf    # Sample PDF for testing
│   ├── sample_student_answers.pdf  # Sample PDF for testing
│   ├── sample_dataset.json
│   └── test_cases.json
├── tests/
│   ├── test_cases.py           # Batch test runner (outputs CSV + JSON)
│   └── test_pdf_pipeline.py    # End-to-end PDF pipeline tests
├── scripts/
│   └── generate_sample_pdfs.py # Generates sample test PDFs
├── results/
│   ├── outputs.json
│   ├── evaluation_metrics.csv
│   └── graphs/
├── notebooks/
│   └── analysis.ipynb
├── render.yaml                 # Render.com deployment config
└── requirements.txt            # Root environment requirements
```

---

## Setup & Run

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
# From project root — activate your virtual environment
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start the backend
uvicorn backend.api.main:app --reload --port 8000
```

The server sets `USE_TF=0` and `TRANSFORMERS_NO_TF=1` automatically to avoid Keras 3 conflicts. The `paraphrase-MiniLM-L3-v2` model is downloaded on first run (~60 MB) and cached locally.

Interactive API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

---

## API Endpoints

### `GET /health`
Returns `{"status": "healthy"}`. Use to confirm the server is up.

---

### `POST /evaluate`
Evaluate a single answer.

**Request:**
```json
{
  "question": "What is machine learning?",
  "model_answer": "Machine learning is a subset of AI...",
  "student_answer": "ML is a branch of AI that learns from data...",
  "model_name": "minilm",
  "max_score": 10
}
```

**Response:**
```json
{
  "question": "What is machine learning?",
  "score": 7.45,
  "max_score": 10,
  "score_label": "Good",
  "similarity": 78.0,
  "keyword_coverage": 40.0,
  "feedback": {
    "strengths": ["Overall semantic meaning is well captured."],
    "missing": ["Missing keywords: subset, experience, improve."],
    "improvements": ["Include more domain-specific terminology."]
  },
  "sentence_analysis": [
    {
      "student_sentence": "...",
      "closest_model_sentence": "...",
      "similarity": 0.82,
      "classification": "strong"
    }
  ],
  "model_keywords": ["machine", "learning", "subset", "..."],
  "summary": "Score: 7.45/10 (Good). Semantic similarity: 78.0%...",
  "ai_detection": {
    "ai_score": 0.21,
    "ai_probability_pct": 21.0,
    "verdict": "Likely Human-written",
    "signals": {
      "burstiness": 0.3,
      "filler_phrases": 0.0,
      "vocabulary_richness": 0.2,
      "avg_word_length": 0.4,
      "transition_density": 0.1,
      "formality": 0.8
    }
  }
}
```

---

### `POST /evaluate-batch`
Evaluate multiple answers in one request.

**Request:**
```json
{
  "student_name": "Alice",
  "items": [
    {
      "question": "...",
      "model_answer": "...",
      "student_answer": "...",
      "max_score": 10
    }
  ]
}
```

**Response:** includes `student_name`, `total_questions`, `average_score_pct`, `average_ai_probability_pct`, and a `results` array of per-question `EvaluateResponse` objects.

---

### `POST /evaluate-pdf`
Upload two PDFs (model answers + student answers), get JSON results.

**Form fields:** `model_pdf` (file), `student_pdf` (file), `student_name` (string), `max_score` (float)

**Expected PDF format:**
```
Q1: What is machine learning?
A1: Machine learning is a subset of AI...

Q2: Explain photosynthesis.
A2: Photosynthesis is the process...
```

Also accepts `Question 1:` / `Answer 1:` format.

---

### `POST /evaluate-pdf/report`
Same as `/evaluate-pdf` but returns a formatted PDF report as a file download instead of JSON.

---

## Scoring Formula

```
final_score = (0.7 × semantic_similarity + 0.3 × keyword_coverage) × max_score
```

Semantic similarity is computed via cosine similarity on transformer embeddings. Keyword coverage measures what fraction of the model answer's key terms appear in the student answer.

**Score labels:**

| Score % | Label         |
|---------|---------------|
| ≥ 85%   | Excellent     |
| ≥ 70%   | Good          |
| ≥ 50%   | Average       |
| ≥ 30%   | Below Average |
| < 30%   | Poor          |

---

## Embedding Model

The backend loads `paraphrase-MiniLM-L3-v2` via `sentence-transformers`. If the model fails to load (e.g. OOM on a free-tier server), it falls back to TF-IDF cosine similarity automatically.

The `model_name` parameter (`minilm` / `bert` / `roberta`) is accepted by the API for forward compatibility but currently all requests use the same loaded model.

---

## AI Detection

The AI detector runs entirely locally with no external API. It scores text on six heuristic signals:

| Signal | What it measures |
|---|---|
| Burstiness | Uniform sentence length (low = AI-like) |
| Filler phrases | Common LLM boilerplate ("it is important to note", etc.) |
| Vocabulary richness | Low type-token ratio (repetitive = AI-like) |
| Avg word length | Longer formal words (AI-like) |
| Transition density | Overuse of "however", "therefore", etc. |
| Formality | Absence of contractions |

Weighted composite score → verdict: Human-written / Likely Human-written / Possibly AI-assisted / Likely AI-generated.

---

## Testing

### End-to-end PDF pipeline tests
```bash
# Backend must be running on port 8000
python tests/test_pdf_pipeline.py
```

### Batch evaluation test suite
```bash
python tests/test_cases.py
# Outputs: results/outputs.json, results/evaluation_metrics.csv
```

### Generate sample PDFs
```bash
python scripts/generate_sample_pdfs.py
# Outputs: data/sample_model_answers.pdf, data/sample_student_answers.pdf
```

---

## Deployment

Configured for [Render.com](https://render.com) via `render.yaml`:

```yaml
services:
  - type: web
    name: evalai-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.13
```

Set `VITE_API_URL` in the frontend environment to point to your deployed backend URL.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, Framer Motion, Axios |
| Backend | FastAPI, Pydantic v2, Uvicorn |
| NLP | sentence-transformers (`paraphrase-MiniLM-L3-v2`), scikit-learn |
| PDF | PyMuPDF (parsing), fpdf2 (generation) |
| Deployment | Render.com |
