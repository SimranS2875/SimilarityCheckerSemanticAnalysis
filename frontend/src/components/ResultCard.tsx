import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { EvaluateResponse, SentenceMatch } from "../services/api";
import FeedbackList from "./FeedbackList";
import { Brain, Tag, ChevronDown, TrendingUp, Percent, Hash, Bot } from "lucide-react";

interface Props { result: EvaluateResponse }

function ScoreRing({ score, max }: { score: number; max: number }) {
  const pct  = score / max;
  const size = 160;
  const r    = 64;
  const cx   = size / 2;
  const circ = 2 * Math.PI * r;
  const color =
    pct >= 0.75 ? { stroke: "#10b981", glow: "rgba(16,185,129,0.4)",  label: "text-emerald-400" } :
    pct >= 0.45 ? { stroke: "#f59e0b", glow: "rgba(245,158,11,0.4)",  label: "text-amber-400"  } :
                  { stroke: "#f43f5e", glow: "rgba(244,63,94,0.4)",   label: "text-rose-400"   };
  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <div className="absolute inset-0 rounded-full blur-xl opacity-30 animate-glow" style={{ background: color.glow }} />
      <svg width={size} height={size} className="-rotate-90 absolute inset-0">
        <circle cx={cx} cy={cx} r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
        <motion.circle
          cx={cx} cy={cx} r={r} fill="none"
          stroke={color.stroke} strokeWidth="8" strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ * (1 - pct) }}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
          style={{ filter: `drop-shadow(0 0 8px ${color.stroke})` }}
        />
      </svg>
      <div className="relative flex flex-col items-center z-10">
        <motion.span
          className={`text-4xl font-extrabold font-mono ${color.label}`}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
        >
          {score}
        </motion.span>
        <span className="text-xs text-slate-500 font-medium">/ {max}</span>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon: Icon, colorClass, delay }: {
  label: string; value: string; icon: React.ElementType; colorClass: string; delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="card flex-1 min-w-[120px] p-4 flex flex-col gap-2"
    >
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-white/5 ${colorClass}`}>
        <Icon size={14} />
      </div>
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-widest">{label}</p>
        <p className={`text-2xl font-bold font-mono mt-0.5 ${colorClass}`}>{value}</p>
      </div>
    </motion.div>
  );
}

const sentenceStyles: Record<string, { bar: string; badge: string; label: string }> = {
  strong:     { bar: "bg-emerald-500", badge: "bg-emerald-500/15 text-emerald-300 border-emerald-500/25", label: "Strong" },
  moderate:   { bar: "bg-sky-500",     badge: "bg-sky-500/15 text-sky-300 border-sky-500/25",             label: "Moderate" },
  weak:       { bar: "bg-amber-500",   badge: "bg-amber-500/15 text-amber-300 border-amber-500/25",       label: "Weak" },
  irrelevant: { bar: "bg-rose-500",    badge: "bg-rose-500/15 text-rose-300 border-rose-500/25",          label: "Irrelevant" },
};

function SentenceRow({ match, idx }: { match: SentenceMatch; idx: number }) {
  const s   = sentenceStyles[match.classification] ?? sentenceStyles.weak;
  const pct = match.similarity * 100;
  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
      transition={{ delay: idx * 0.07 }}
      className="card p-4 flex flex-col gap-3"
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-mono">#{idx + 1}</span>
          <span className={`tag border ${s.badge} font-semibold`}>{s.label}</span>
        </div>
        <div className="flex items-center gap-2 ml-auto">
          <div className="w-24 h-1.5 rounded-full bg-white/5 overflow-hidden">
            <motion.div
              className={`h-full rounded-full ${s.bar}`}
              initial={{ width: 0 }}
              animate={{ width: `${pct}%` }}
              transition={{ delay: idx * 0.07 + 0.2, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            />
          </div>
          <span className="text-xs font-mono text-slate-400">{pct.toFixed(0)}%</span>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="rounded-xl bg-white/[0.02] border border-white/5 p-3">
          <p className="text-[10px] uppercase tracking-widest text-slate-600 mb-1.5">Student</p>
          <p className="text-sm text-slate-300 leading-relaxed">{match.student_sentence}</p>
        </div>
        <div className="rounded-xl bg-white/[0.02] border border-white/5 p-3">
          <p className="text-[10px] uppercase tracking-widest text-slate-600 mb-1.5">Closest Model</p>
          <p className="text-sm text-slate-400 leading-relaxed">{match.closest_model_sentence}</p>
        </div>
      </div>
    </motion.div>
  );
}

function Accordion({ title, icon: Icon, children }: {
  title: string; icon: React.ElementType; children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 text-sm font-semibold
                   text-slate-300 hover:text-white hover:bg-white/[0.03] transition-all duration-200"
      >
        <span className="flex items-center gap-2.5">
          <Icon size={15} className="text-sky-400" />
          {title}
        </span>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={15} className="text-slate-500" />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-1 border-t border-white/5">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function ResultCard({ result }: Props) {
  const pct = result.score / result.max_score;
  const gradeColor =
    pct >= 0.75 ? "text-emerald-400" :
    pct >= 0.45 ? "text-amber-400"   : "text-rose-400";
  const barGradient =
    pct >= 0.75 ? "linear-gradient(90deg,#059669,#10b981,#34d399)" :
    pct >= 0.45 ? "linear-gradient(90deg,#d97706,#f59e0b,#fbbf24)" :
                  "linear-gradient(90deg,#be123c,#f43f5e,#fb7185)";
  const missingKws = result.feedback.missing
    .filter((m) => m.startsWith("Missing keywords:"))
    .flatMap((m) =>
      m.replace("Missing keywords:", "").trim().replace(/\.$/, "").split(",").map((k) => k.trim()).filter(Boolean)
    );

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col gap-5">

      {/* Hero score card */}
      <motion.div
        initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="card p-6 md:p-8"
      >
        <div className="flex flex-wrap items-center gap-8">
          <ScoreRing score={result.score} max={result.max_score} />
          <div className="flex flex-col gap-2 flex-1 min-w-[180px]">
            <motion.div initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>
              <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">Overall Grade</p>
              <p className={`text-5xl font-extrabold leading-none ${gradeColor}`}>{result.score_label}</p>
            </motion.div>
            <motion.p
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
              className="text-sm text-slate-400 leading-relaxed max-w-sm"
            >
              {result.summary}
            </motion.p>
          </div>
          <div className="flex flex-wrap gap-3 ml-auto">
            <StatCard label="Similarity" value={`${result.similarity}%`}               icon={Percent}    colorClass="text-sky-400" delay={0.4} />
            <StatCard label="Keywords"   value={`${result.keyword_coverage}%`}         icon={Hash}       colorClass="text-sky-400"    delay={0.5} />
            <StatCard label="Score"      value={`${result.score}/${result.max_score}`} icon={TrendingUp} colorClass={gradeColor}      delay={0.6} />
            {result.ai_detection && (
              <StatCard
                label="AI Probability"
                value={`${result.ai_detection.ai_probability_pct}%`}
                icon={Bot}
                colorClass={result.ai_detection.ai_probability_pct >= 75 ? "text-rose-400" : result.ai_detection.ai_probability_pct >= 50 ? "text-amber-400" : "text-emerald-400"}
                delay={0.7}
              />
            )}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-6">
          <div className="flex justify-between text-xs text-slate-500 mb-2">
            <span>Score Progress</span>
            <span className="font-mono">{Math.round(pct * 100)}%</span>
          </div>
          <div className="h-2 rounded-full bg-white/5 overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${pct * 100}%` }}
              transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1], delay: 0.4 }}
              style={{ background: barGradient, boxShadow: `0 0 12px ${pct >= 0.75 ? "#10b981" : pct >= 0.45 ? "#f59e0b" : "#f43f5e"}60` }}
            />
          </div>
        </div>
      </motion.div>

      {/* Feedback */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <FeedbackList
          strengths={result.feedback.strengths}
          missing={result.feedback.missing}
          improvements={result.feedback.improvements}
        />
      </motion.div>

      {/* Keywords accordion */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Accordion title="Keyword Analysis" icon={Tag}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-600 mb-3">Model Keywords</p>
              <div className="flex flex-wrap gap-2">
                {result.model_keywords.map((kw) => (
                  <span key={kw} className="tag bg-sky-500/10 border-sky-500/20 text-sky-300">{kw}</span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-600 mb-3">Missing Keywords</p>
              <div className="flex flex-wrap gap-2">
                {missingKws.length === 0
                  ? <span className="text-xs text-slate-600 italic">None missing</span>
                  : missingKws.map((kw) => (
                      <span key={kw} className="tag bg-rose-500/10 border-rose-500/20 text-rose-300">{kw}</span>
                    ))
                }
              </div>
            </div>
          </div>
        </Accordion>
      </motion.div>

      {/* Sentence analysis accordion */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <Accordion title="Sentence-Level Analysis" icon={Brain}>
          <div className="flex flex-col gap-3 pt-2">
            {result.sentence_analysis.length === 0
              ? <p className="text-sm text-slate-600 italic">No sentence data available.</p>
              : result.sentence_analysis.map((s, i) => <SentenceRow key={i} match={s} idx={i} />)
            }
          </div>
        </Accordion>
      </motion.div>
    </motion.div>
  );
}
