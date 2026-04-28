import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { BatchResponse, EvaluateResponse } from "../services/api";
import FeedbackList from "./FeedbackList";
import { ChevronDown, Brain, Bot, TrendingUp, FileDown } from "lucide-react";

interface Props {
  batch: BatchResponse;
  onDownloadPDF: () => void;
  downloading: boolean;
}

function AIBadge({ pct, verdict }: { pct: number; verdict: string }) {
  const color =
    pct >= 75 ? "bg-rose-500/15 border-rose-500/25 text-rose-300" :
    pct >= 50 ? "bg-amber-500/15 border-amber-500/25 text-amber-300" :
                "bg-emerald-500/15 border-emerald-500/25 text-emerald-300";
  return (
    <span className={`tag border ${color} flex items-center gap-1.5`}>
      <Bot size={11} />
      {pct.toFixed(1)}% — {verdict}
    </span>
  );
}

function ScoreBar({ pct }: { pct: number }) {
  const grad =
    pct >= 75 ? "linear-gradient(90deg,#059669,#10b981)" :
    pct >= 45 ? "linear-gradient(90deg,#d97706,#f59e0b)" :
                "linear-gradient(90deg,#be123c,#f43f5e)";
  return (
    <div className="h-1.5 rounded-full bg-white/5 overflow-hidden w-full">
      <motion.div
        className="h-full rounded-full"
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        style={{ background: grad }}
      />
    </div>
  );
}

function QuestionCard({ result, idx }: { result: EvaluateResponse; idx: number }) {
  const [open, setOpen] = useState(false);
  const scorePct = (result.score / result.max_score) * 100;
  const scoreColor =
    scorePct >= 75 ? "text-emerald-400" :
    scorePct >= 45 ? "text-amber-400"   : "text-rose-400";

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.08 }}
      className="card overflow-hidden"
    >
      {/* Header row */}
      <button
        onClick={() => setOpen(!open)}
        className="w-full px-5 py-4 flex flex-wrap items-center gap-4 hover:bg-white/[0.02] transition-colors text-left"
      >
        {/* Q number */}
        <span className="w-8 h-8 rounded-lg bg-sky-500/15 flex items-center justify-center text-sky-400 text-xs font-bold shrink-0">
          Q{idx + 1}
        </span>

        {/* Question text */}
        <span className="flex-1 text-sm text-slate-300 font-medium min-w-0 truncate">
          {result.question || `Question ${idx + 1}`}
        </span>

        {/* Score */}
        <span className={`font-mono font-bold text-lg shrink-0 ${scoreColor}`}>
          {result.score}/{result.max_score}
        </span>

        {/* AI badge */}
        <AIBadge pct={result.ai_detection.ai_probability_pct} verdict={result.ai_detection.verdict} />

        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={15} className="text-slate-500 shrink-0" />
        </motion.div>
      </button>

      {/* Score bar */}
      <div className="px-5 pb-3">
        <ScoreBar pct={scorePct} />
      </div>

      {/* Expanded detail */}
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 border-t border-white/5 pt-4 flex flex-col gap-4">
              {/* Metrics */}
              <div className="flex flex-wrap gap-3">
                {[
                  { label: "Semantic Similarity", value: `${result.similarity}%`, color: "text-violet-400" },
                  { label: "Keyword Coverage",    value: `${result.keyword_coverage}%`, color: "text-sky-400" },
                  { label: "Grade",               value: result.score_label, color: scoreColor },
                ].map((m) => (
                  <div key={m.label} className="card px-4 py-3 rounded-xl flex flex-col gap-0.5">
                    <p className="text-xs text-slate-500 uppercase tracking-widest">{m.label}</p>
                    <p className={`text-lg font-bold font-mono ${m.color}`}>{m.value}</p>
                  </div>
                ))}
              </div>

              {/* AI signals */}
              <div className="card rounded-xl px-4 py-3">
                <p className="text-xs uppercase tracking-widest text-slate-500 mb-2 flex items-center gap-1.5">
                  <Bot size={11} /> AI Detection Signals
                </p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(result.ai_detection.signals).map(([k, v]) => (
                    <span key={k} className="tag bg-white/5 border-white/10 text-slate-400">
                      {k.replace(/_/g, " ")}: <span className="font-mono text-slate-300">{(v * 100).toFixed(0)}%</span>
                    </span>
                  ))}
                </div>
              </div>

              {/* Feedback */}
              <FeedbackList
                strengths={result.feedback.strengths}
                missing={result.feedback.missing}
                improvements={result.feedback.improvements}
              />

              {/* Sentence analysis */}
              {result.sentence_analysis.length > 0 && (
                <div>
                  <p className="text-xs uppercase tracking-widest text-slate-500 mb-2 flex items-center gap-1.5">
                    <Brain size={11} /> Sentence Analysis
                  </p>
                  <div className="flex flex-col gap-2">
                    {result.sentence_analysis.map((s, i) => {
                      const cls = s.classification;
                      const c =
                        cls === "strong"     ? "border-emerald-500/20 text-emerald-300" :
                        cls === "moderate"   ? "border-sky-500/20 text-sky-300"         :
                        cls === "weak"       ? "border-amber-500/20 text-amber-300"     :
                                               "border-rose-500/20 text-rose-300";
                      return (
                        <div key={i} className={`card rounded-xl p-3 border ${c} text-xs`}>
                          <div className="flex justify-between mb-1">
                            <span className="font-semibold uppercase tracking-wider">{cls}</span>
                            <span className="font-mono">{(s.similarity * 100).toFixed(0)}%</span>
                          </div>
                          <p className="text-slate-400">{s.student_sentence}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function BatchResultCard({ batch, onDownloadPDF, downloading }: Props) {
  const scoreColor =
    batch.average_score_pct >= 75 ? "text-emerald-400" :
    batch.average_score_pct >= 45 ? "text-amber-400"   : "text-rose-400";
  const aiColor =
    batch.average_ai_probability_pct >= 75 ? "text-rose-400" :
    batch.average_ai_probability_pct >= 50 ? "text-amber-400" : "text-emerald-400";

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col gap-5">

      {/* Summary card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="card p-6 md:p-8"
      >
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">Student</p>
            <p className="text-3xl font-extrabold text-white">{batch.student_name}</p>
            <p className="text-sm text-slate-500 mt-1">{batch.total_questions} question{batch.total_questions !== 1 ? "s" : ""} evaluated</p>
          </div>

          <div className="flex flex-wrap gap-4">
            <div className="card px-5 py-4 rounded-xl flex flex-col gap-1">
              <p className="text-xs text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <TrendingUp size={11} /> Avg Score
              </p>
              <p className={`text-3xl font-extrabold font-mono ${scoreColor}`}>
                {batch.average_score_pct.toFixed(1)}%
              </p>
            </div>
            <div className="card px-5 py-4 rounded-xl flex flex-col gap-1">
              <p className="text-xs text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                <Bot size={11} /> Avg AI Probability
              </p>
              <p className={`text-3xl font-extrabold font-mono ${aiColor}`}>
                {batch.average_ai_probability_pct.toFixed(1)}%
              </p>
            </div>
          </div>

          {/* Download PDF */}
          <button
            onClick={onDownloadPDF}
            disabled={downloading}
            className="btn-primary w-auto px-6 py-3 text-sm"
          >
            {downloading ? (
              <>
                <motion.div
                  className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
                />
                Generating…
              </>
            ) : (
              <>
                <FileDown size={15} />
                Download PDF Report
              </>
            )}
          </button>
        </div>

        {/* Overall score bar */}
        <div className="mt-6">
          <div className="flex justify-between text-xs text-slate-500 mb-2">
            <span>Overall Performance</span>
            <span className="font-mono">{batch.average_score_pct.toFixed(1)}%</span>
          </div>
          <ScoreBar pct={batch.average_score_pct} />
        </div>
      </motion.div>

      {/* Per-question cards */}
      <div className="flex flex-col gap-3">
        {batch.results.map((r, i) => (
          <QuestionCard key={i} result={r} idx={i} />
        ))}
      </div>
    </motion.div>
  );
}
