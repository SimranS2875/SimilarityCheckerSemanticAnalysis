import { useState } from "react";
import type { EvaluateRequest } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ChevronDown, AlertCircle } from "lucide-react";

interface Props {
  onSubmit: (req: EvaluateRequest) => void;
  loading: boolean;
}

const MODELS = [
  { value: "minilm",  label: "MiniLM-L3",  desc: "Fastest · Recommended" },
  { value: "bert",    label: "MiniLM-L3",  desc: "Balanced accuracy" },
  { value: "roberta", label: "MiniLM-L3",  desc: "Highest accuracy" },
];

export default function InputForm({ onSubmit, loading }: Props) {
  const [question, setQuestion]       = useState("");
  const [modelAnswer, setModelAnswer] = useState("");
  const [studentAnswer, setStudentAnswer] = useState("");
  const [modelName, setModelName]     = useState("minilm");
  const [maxScore, setMaxScore]       = useState(10);
  const [error, setError]             = useState("");
  const [focused, setFocused]         = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!modelAnswer.trim() || !studentAnswer.trim()) {
      setError("Both model answer and student answer are required.");
      return;
    }
    setError("");
    onSubmit({ question, model_answer: modelAnswer, student_answer: studentAnswer, model_name: modelName, max_score: maxScore });
  }

  const pct = (maxScore / 100) * 100;

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-7">

      {/* ── Top config row ── */}
      <div className="flex flex-wrap gap-4 items-end">
        {/* Model selector */}
        <div className="flex flex-col gap-2 flex-1 min-w-[200px]">
          <label className="label">Embedding Model</label>
          <div className="relative">
            <select
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              className="input-field appearance-none pr-9 cursor-pointer font-medium"            >
              {MODELS.map((m) => (
                <option key={m.value} value={m.value}>{m.label} — {m.desc}</option>
              ))}
            </select>
            <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
          </div>
        </div>

        {/* Max score */}
        <div className="flex flex-col gap-2 flex-1 min-w-[200px]">
          <label className="label flex items-center justify-between">
            <span>Max Score</span>
            <span className="text-violet-400 font-mono font-bold text-sm normal-case tracking-normal">{maxScore}</span>
          </label>
          <div className="relative h-10 flex items-center">
            <div className="absolute inset-x-0 h-1.5 rounded-full bg-white/5" />
            <div
              className="absolute left-0 h-1.5 rounded-full transition-all duration-200"
              style={{ width: `${pct}%`, background: "linear-gradient(90deg,#0ea5e9,#0284c7)" }}
            />
            <input
              type="range" min={5} max={100} step={5}
              value={maxScore}
              onChange={(e) => setMaxScore(Number(e.target.value))}
              className="relative w-full appearance-none bg-transparent cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:shadow-lg
                [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-sky-400
                [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:transition-transform
                [&::-webkit-slider-thumb]:hover:scale-125"
            />
          </div>
        </div>
      </div>

      {/* ── Question ── */}
      <div>
        <label className="label">
          Question
          <span className="ml-2 normal-case tracking-normal text-slate-600 font-normal">optional</span>
        </label>
        <div className={`relative rounded-xl transition-all duration-200 ${focused === "q" ? "ring-2 ring-sky-500/20" : ""}`}>
          <textarea
            rows={2}
            className="input-field"
            placeholder="e.g. What is machine learning?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onFocus={() => setFocused("q")}
            onBlur={() => setFocused(null)}
          />
        </div>
      </div>

      {/* ── Two-column answers ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Model answer */}
        <div className="flex flex-col gap-2">
          <label className="label flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" />
            Model Answer
            <span className="text-rose-400 font-bold">*</span>
          </label>
          <div className={`relative rounded-xl transition-all duration-200 ${focused === "ma" ? "ring-2 ring-sky-500/20" : ""}`}>
            <textarea
              rows={9}
              className="input-field"
              placeholder="Enter the reference / ideal answer…"
              value={modelAnswer}
              onChange={(e) => setModelAnswer(e.target.value)}
              onFocus={() => setFocused("ma")}
              onBlur={() => setFocused(null)}
            />
            {modelAnswer && (
              <div className="absolute bottom-3 right-3 text-xs text-slate-600 font-mono">
                {modelAnswer.split(/\s+/).filter(Boolean).length}w
              </div>
            )}
          </div>
        </div>

        {/* Student answer */}
        <div className="flex flex-col gap-2">
          <label className="label flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-violet-400 inline-block" />
            Student Answer
            <span className="text-rose-400 font-bold">*</span>
          </label>
          <div className={`relative rounded-xl transition-all duration-200 ${focused === "sa" ? "ring-2 ring-sky-500/20" : ""}`}>
            <textarea
              rows={9}
              className="input-field"
              placeholder="Enter the student's answer…"
              value={studentAnswer}
              onChange={(e) => setStudentAnswer(e.target.value)}
              onFocus={() => setFocused("sa")}
              onBlur={() => setFocused(null)}
            />
            {studentAnswer && (
              <div className="absolute bottom-3 right-3 text-xs text-slate-600 font-mono">
                {studentAnswer.split(/\s+/).filter(Boolean).length}w
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Error ── */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="flex items-center gap-3 px-4 py-3 rounded-xl bg-rose-500/8 border border-rose-500/20 text-rose-300 text-sm"
          >
            <AlertCircle size={15} className="shrink-0" />
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Submit ── */}
      <button type="submit" disabled={loading} className="btn-primary">
        {loading ? (
          <>
            <motion.div
              className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white"
              animate={{ rotate: 360 }}
              transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
            />
            Evaluating…
          </>
        ) : (
          <>
            <Sparkles size={16} />
            Evaluate Answer
          </>
        )}
      </button>
    </form>
  );
}
