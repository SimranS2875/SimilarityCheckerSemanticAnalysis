import axios from "axios";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface EvaluateRequest {
  question: string;
  model_answer: string;
  student_answer: string;
  model_name?: string;
  max_score?: number;
}

export interface SentenceMatch {
  student_sentence: string;
  closest_model_sentence: string;
  similarity: number;
  classification: "strong" | "moderate" | "weak" | "irrelevant";
}

export interface EvaluateResponse {
  score: number;
  max_score: number;
  score_label: string;
  similarity: number;
  keyword_coverage: number;
  feedback: {
    strengths: string[];
    missing: string[];
    improvements: string[];
  };
  sentence_analysis: SentenceMatch[];
  model_keywords: string[];
  summary: string;
}

export async function evaluateAnswer(req: EvaluateRequest): Promise<EvaluateResponse> {
  const { data } = await axios.post<EvaluateResponse>(`${BASE}/evaluate`, req);
  return data;
}
