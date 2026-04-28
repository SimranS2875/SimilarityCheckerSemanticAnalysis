import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import InputForm from "./components/InputForm";
import ResultCard from "./components/ResultCard";
import PDFUploadForm from "./components/PDFUploadForm";
import BatchResultCard from "./components/BatchResultCard";
import Loader from "./components/Loader";
import {
  evaluateAnswer, evaluatePDF, downloadPDFReport,
  type EvaluateRequest, type EvaluateResponse, type BatchResponse,
} from "./services/api";
import { GraduationCap, Layers, FileText } from "lucide-react";

/* ── Background ───────────────────────────────────────────────────────────── */
function Background() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none" aria-hidden>
      <div className="absolute inset-0" style={{
        background: "radial-gradient(ellipse 80% 50% at 50% -5%, rgba(14,165,233,0.1) 0%, transparent 70%)"
      }} />
      <motion.div
        className="absolute w-[600px] h-[600px] rounded-full blur-[130px] opacity-15"
        style={{ background: "radial-gradient(circle, #0ea5e9, transparent)", top: "-15%", left: "-10%" }}
        animate={{ x: [0, 40, 0], y: [0, 25, 0] }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-[500px] h-[500px] rounded-full blur-[110px] opacity-10"
        style={{ background: "radial-gradient(circle, #f59e0b, transparent)", bottom: "5%", right: "-8%" }}
        animate={{ x: [0, -25, 0], y: [0, -35, 0] }}
        transition={{ duration: 16, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-[350px] h-[350px] rounded-full blur-[90px] opacity-10"
        style={{ background: "radial-gradient(circle, #6366f1, transparent)", top: "45%", left: "55%" }}
        animate={{ x: [0, 20, 0], y: [0, -20, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />
      <div className="absolute inset-0 opacity-[0.02]" style={{
        backgroundImage: "linear-gradient(rgba(56,189,248,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(56,189,248,0.8) 1px, transparent 1px)",
        backgroundSize: "64px 64px"
      }} />
    </div>
  );
}

/* ── Hero ─────────────────────────────────────────────────────────────────── */
function Hero({ onStart }: { onStart: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center text-center gap-10 py-16 md:py-24"
    >
      <motion.div
        initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-sky-500/20 bg-sky-500/8 text-sky-300 text-xs font-semibold tracking-wide"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse" />
        NLP · Semantic Similarity · Transformer-Based
      </motion.div>

      <div className="flex flex-col gap-4">
        <motion.h1
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="text-5xl md:text-7xl font-extrabold leading-[1.05] tracking-tight"
        >
          <span className="text-white">Automated</span>
          <br />
          <span className="shimmer-text">Answer Evaluation</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
          className="text-slate-400 text-lg md:text-xl max-w-xl mx-auto leading-relaxed"
        >
          Score descriptive answers intelligently using transformer models. Upload PDFs for batch evaluation with AI detection.
        </motion.p>
      </div>

      <motion.button
        initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}
        onClick={onStart}
        className="btn-primary w-auto px-10 py-4 text-base"
      >
        Start Evaluating
      </motion.button>
    </motion.div>
  );
}

/* ── Tab button ───────────────────────────────────────────────────────────── */
function Tab({ active, onClick, icon: Icon, label }: {
  active: boolean; onClick: () => void; icon: React.ElementType; label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200
        ${active
          ? "bg-sky-500/15 border border-sky-500/30 text-sky-300"
          : "text-slate-500 hover:text-slate-300 border border-transparent"
        }`}
    >
      <Icon size={15} />
      {label}
    </button>
  );
}

/* ── App ──────────────────────────────────────────────────────────────────── */
export default function App() {
  const [tab, setTab]             = useState<"single" | "pdf">("single");
  const [result, setResult]       = useState<EvaluateResponse | null>(null);
  const [batch, setBatch]         = useState<BatchResponse | null>(null);
  const [loading, setLoading]     = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError]         = useState("");
  const formRef                   = useRef<HTMLDivElement>(null);

  // Store last PDF inputs for report download
  const lastPDFRef = useRef<{ modelPdf: File; studentPdf: File; studentName: string; maxScore: number } | null>(null);

  function reset() { setResult(null); setBatch(null); setError(""); }

  async function handleSingle(req: EvaluateRequest) {
    setLoading(true); reset();
    try {
      const res = await evaluateAnswer(req);
      setResult(res);
    } catch (e: unknown) {
      setError((e as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail ?? (e as { message?: string })?.message ?? "Evaluation failed.");
    } finally { setLoading(false); }
  }

  async function handlePDF(modelPdf: File, studentPdf: File, studentName: string, maxScore: number) {
    setLoading(true); reset();
    lastPDFRef.current = { modelPdf, studentPdf, studentName, maxScore };
    try {
      const res = await evaluatePDF(modelPdf, studentPdf, studentName, maxScore);
      setBatch(res);
    } catch (e: unknown) {
      setError((e as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail ?? (e as { message?: string })?.message ?? "PDF evaluation failed.");
    } finally { setLoading(false); }
  }

  async function handleDownloadPDF() {
    if (!lastPDFRef.current) return;
    setDownloading(true);
    try {
      const { modelPdf, studentPdf, studentName, maxScore } = lastPDFRef.current;
      const blob = await downloadPDFReport(modelPdf, studentPdf, studentName, maxScore);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `evaluation_report_${studentName}.pdf`;
      a.click(); URL.revokeObjectURL(url);
    } catch { setError("Failed to generate PDF report."); }
    finally { setDownloading(false); }
  }

  return (
    <div className="min-h-screen font-sans">
      <Background />
      <div className="relative z-10 max-w-6xl mx-auto px-4 md:px-6">

        {/* Nav */}
        <motion.nav
          initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between py-5 border-b border-white/5"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sky-400 to-blue-600 flex items-center justify-center" style={{ boxShadow: "0 0 16px rgba(14,165,233,0.35)" }}>
              <GraduationCap size={16} />
            </div>
            <span className="font-bold text-sm text-white">EvalAI</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse" />
            FastAPI · React · Sentence Transformers
          </div>
        </motion.nav>

        {/* Hero */}
        <Hero onStart={() => formRef.current?.scrollIntoView({ behavior: "smooth" })} />

        {/* Divider */}
        <div className="flex items-center gap-4 mb-8">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
          <span className="text-xs text-slate-600 uppercase tracking-widest">Evaluation</span>
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        </div>

        {/* Form card */}
        <div ref={formRef}>
          <motion.div
            initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }} transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="card p-6 md:p-8 mb-8"
          >
            {/* Header + tabs */}
            <div className="flex flex-wrap items-center justify-between gap-4 mb-7">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-sky-500/15 flex items-center justify-center text-sky-400">
                  <Layers size={16} />
                </div>
                <div>
                  <h2 className="font-bold text-white text-base">Evaluate Answers</h2>
                  <p className="text-xs text-slate-500">Single answer or batch PDF upload</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Tab active={tab === "single"} onClick={() => { setTab("single"); reset(); }} icon={Layers}    label="Single Answer" />
                <Tab active={tab === "pdf"}    onClick={() => { setTab("pdf");    reset(); }} icon={FileText}  label="PDF Upload" />
              </div>
            </div>

            <AnimatePresence mode="wait">
              {tab === "single" ? (
                <motion.div key="single" initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 12 }}>
                  <InputForm onSubmit={handleSingle} loading={loading} />
                </motion.div>
              ) : (
                <motion.div key="pdf" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }}>
                  <PDFUploadForm onSubmit={handlePDF} loading={loading} />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>

        {/* States */}
        <AnimatePresence mode="wait">
          {loading && (
            <motion.div key="loader" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <Loader />
            </motion.div>
          )}

          {error && !loading && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="card border-rose-500/25 p-5 flex items-start gap-3 text-rose-300 text-sm mb-8"
            >
              <span className="text-rose-400 text-lg leading-none">⚠</span>
              <div>
                <p className="font-semibold mb-0.5">Evaluation failed</p>
                <p className="text-rose-400/70 text-xs">{error}</p>
              </div>
            </motion.div>
          )}

          {result && !loading && (
            <motion.div key="result" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-16">
              <div className="flex items-center gap-4 mb-6">
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                <span className="text-xs text-slate-600 uppercase tracking-widest">Results</span>
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
              </div>
              <ResultCard result={result} />
            </motion.div>
          )}

          {batch && !loading && (
            <motion.div key="batch" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-16">
              <div className="flex items-center gap-4 mb-6">
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                <span className="text-xs text-slate-600 uppercase tracking-widest">Batch Results</span>
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
              </div>
              <BatchResultCard batch={batch} onDownloadPDF={handleDownloadPDF} downloading={downloading} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
