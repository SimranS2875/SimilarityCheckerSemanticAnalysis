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

export interface AIDetection {
  ai_score: number;
  ai_probability_pct: number;
  verdict: string;
  signals: Record<string, number>;
}

export interface EvaluateResponse {
  question: string;
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
  ai_detection: AIDetection;
}

export interface BatchResponse {
  student_name: string;
  total_questions: number;
  average_score_pct: number;
  average_ai_probability_pct: number;
  results: EvaluateResponse[];
}

export async function evaluateAnswer(req: EvaluateRequest): Promise<EvaluateResponse> {
  const { data } = await axios.post<EvaluateResponse>(`${BASE}/evaluate`, req);
  return data;
}

export async function evaluatePDF(
  modelPdf: File,
  studentPdf: File,
  studentName: string,
  maxScore: number,
): Promise<BatchResponse> {
  const form = new FormData();
  form.append("model_pdf", modelPdf);
  form.append("student_pdf", studentPdf);
  form.append("student_name", studentName);
  form.append("max_score", String(maxScore));
  const { data } = await axios.post<BatchResponse>(`${BASE}/evaluate-pdf`, form);
  return data;
}

export async function downloadPDFReport(
  modelPdf: File,
  studentPdf: File,
  studentName: string,
  maxScore: number,
): Promise<Blob> {
  const form = new FormData();
  form.append("model_pdf", modelPdf);
  form.append("student_pdf", studentPdf);
  form.append("student_name", studentName);
  form.append("max_score", String(maxScore));
  const { data } = await axios.post(`${BASE}/evaluate-pdf/report`, form, {
    responseType: "blob",
  });
  return data;
}
