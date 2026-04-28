import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, Sparkles, User, AlertCircle } from "lucide-react";

interface Props {
  onSubmit: (modelPdf: File, studentPdf: File, studentName: string, maxScore: number) => void;
  loading: boolean;
}

function DropZone({
  label, color, file, onFile, onClear,
}: {
  label: string; color: string; file: File | null;
  onFile: (f: File) => void; onClear: () => void;
}) {
  const ref = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f?.type === "application/pdf") onFile(f);
  }

  return (
    <div className="flex flex-col gap-2 flex-1">
      <label className="label flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full ${color}`} />
        {label}
        <span className="text-rose-400 font-bold">*</span>
      </label>

      {file ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card flex items-center gap-3 px-4 py-4 rounded-xl"
        >
          <FileText size={20} className="text-sky-400 shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-200 truncate">{file.name}</p>
            <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
          <button onClick={onClear} className="text-slate-500 hover:text-rose-400 transition-colors">
            <X size={16} />
          </button>
        </motion.div>
      ) : (
        <div
          onClick={() => ref.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={`relative flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed
            cursor-pointer transition-all duration-200 py-10 px-4
            ${dragging
              ? "border-sky-400 bg-sky-500/8"
              : "border-white/10 hover:border-sky-500/40 hover:bg-sky-500/4"
            }`}
        >
          <Upload size={24} className="text-slate-500" />
          <div className="text-center">
            <p className="text-sm text-slate-400 font-medium">Drop PDF here or click to browse</p>
            <p className="text-xs text-slate-600 mt-1">PDF files only</p>
          </div>
          <input
            ref={ref} type="file" accept=".pdf" className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }}
          />
        </div>
      )}
    </div>
  );
}

export default function PDFUploadForm({ onSubmit, loading }: Props) {
  const [modelPdf, setModelPdf]     = useState<File | null>(null);
  const [studentPdf, setStudentPdf] = useState<File | null>(null);
  const [studentName, setStudentName] = useState("");
  const [maxScore, setMaxScore]     = useState(10);
  const [error, setError]           = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!modelPdf || !studentPdf) {
      setError("Please upload both the model answer PDF and student answer PDF.");
      return;
    }
    setError("");
    onSubmit(modelPdf, studentPdf, studentName || "Student", maxScore);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">

      {/* Config row */}
      <div className="flex flex-wrap gap-4 items-end">
        <div className="flex flex-col gap-2 flex-1 min-w-[200px]">
          <label className="label flex items-center gap-2">
            <User size={12} /> Student Name
            <span className="text-slate-600 normal-case tracking-normal font-normal">optional</span>
          </label>
          <input
            type="text"
            className="input-field"
            placeholder="e.g. Simran"
            value={studentName}
            onChange={(e) => setStudentName(e.target.value)}
          />
        </div>
        <div className="flex flex-col gap-2 flex-1 min-w-[200px]">
          <label className="label flex items-center justify-between">
            <span>Max Score per Question</span>
            <span className="text-sky-400 font-mono font-bold text-sm normal-case tracking-normal">{maxScore}</span>
          </label>
          <div className="relative h-10 flex items-center">
            <div className="absolute inset-x-0 h-1.5 rounded-full bg-white/5" />
            <div
              className="absolute left-0 h-1.5 rounded-full transition-all duration-200"
              style={{ width: `${(maxScore / 100) * 100}%`, background: "linear-gradient(90deg,#0ea5e9,#0284c7)" }}
            />
            <input
              type="range" min={5} max={100} step={5} value={maxScore}
              onChange={(e) => setMaxScore(Number(e.target.value))}
              className="relative w-full appearance-none bg-transparent cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:shadow-lg
                [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-sky-400
                [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:hover:scale-125
                [&::-webkit-slider-thumb]:transition-transform"
            />
          </div>
        </div>
      </div>

      {/* PDF drop zones */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <DropZone
          label="Model Answer PDF"
          color="bg-emerald-400"
          file={modelPdf}
          onFile={setModelPdf}
          onClear={() => setModelPdf(null)}
        />
        <DropZone
          label="Student Answer PDF"
          color="bg-violet-400"
          file={studentPdf}
          onFile={setStudentPdf}
          onClear={() => setStudentPdf(null)}
        />
      </div>

      {/* PDF format hint */}
      <div className="card rounded-xl px-4 py-3 text-xs text-slate-500 leading-relaxed">
        <p className="font-semibold text-slate-400 mb-1">Expected PDF format:</p>
        <p>Q1: What is machine learning?</p>
        <p>A1: Machine learning is a subset of AI...</p>
        <p className="mt-1">Q2: Explain photosynthesis.</p>
        <p>A2: Photosynthesis is the process...</p>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="flex items-center gap-3 px-4 py-3 rounded-xl bg-rose-500/8 border border-rose-500/20 text-rose-300 text-sm"
          >
            <AlertCircle size={15} className="shrink-0" />
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      <button type="submit" disabled={loading} className="btn-primary">
        {loading ? (
          <>
            <motion.div
              className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white"
              animate={{ rotate: 360 }}
              transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
            />
            Evaluating PDFs…
          </>
        ) : (
          <>
            <Sparkles size={16} />
            Evaluate PDFs
          </>
        )}
      </button>
    </form>
  );
}
