# Automated Descriptive Answer Evaluation
### Transformer-Based Semantic Similarity · FastAPI + React

A production-ready full-stack NLP system that evaluates student descriptive answers against a reference answer using transformer embeddings, hybrid scoring, and structured feedback.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React + TypeScript                    │
│              (Vite · Tailwind CSS · Axios)               │
│                   localhost:5173                         │
└──────────────────────┬──────────────────────────────────┘
                       │  POST /evaluate
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│                   localhost:8000                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              NLP Pipeline                       │    │
│  │  Preprocess → Embed → Cosine Sim → Hybrid Score │    │
│  │  Keyword Coverage → Sentence Analysis → Feedback│    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
project/
├── backend/
│   ├── api/
│   │   └── main.py           # FastAPI app + /evaluate endpoint
│   ├── src/
│   │   ├── preprocessing.py
│   │   ├── embedding.py      # SentenceTransformer wrapper
│   │   ├── similarity.py     # Cosine + sentence-level similarity
│   │   ├── scoring.py        # Keyword extraction + hybrid scoring
│   │   ├── feedback.py       # Structured feedback generation
│   │   └── evaluator.py      # Pipeline orchestrator
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InputForm.tsx
│   │   │   ├── ResultCard.tsx
│   │   │   ├── FeedbackList.tsx
│   │   │   └── Loader.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── tailwind.config.js
├── data/
├── tests/
├── notebooks/
├── results/
└── requirements.txt          # Root venv requirements
```

---

## Setup & Run

### 1. Backend

```bash
# From project root, activate venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install fastapi "uvicorn[standard]"

uvicorn backend.api.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

---

## API

### POST /evaluate

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
  "score": 7.45,
  "max_score": 10,
  "score_label": "Good",
  "similarity": 89.3,
  "keyword_coverage": 40.0,
  "feedback": {
    "strengths": ["Overall semantic meaning is well captured."],
    "missing": ["Missing keywords: subset, experience, improve."],
    "improvements": ["Include more domain-specific terminology."]
  },
  "sentence_analysis": [...],
  "model_keywords": ["machine", "learning", "subset", ...],
  "summary": "Score: 7.45/10 (Good). Semantic similarity: 89.3%..."
}
```

---

## Scoring Formula

```
final_score = (0.7 × semantic_similarity + 0.3 × keyword_coverage) × max_score
```

---

## Supported Models

| Alias   | Model                        |
|---------|------------------------------|
| minilm  | all-MiniLM-L6-v2 (default)  |
| bert    | bert-base-nli-mean-tokens    |
| roberta | stsb-roberta-base            |
