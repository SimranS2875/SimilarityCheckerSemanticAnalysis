import { motion } from "framer-motion";

const steps = ["Preprocessing text…", "Generating embeddings…", "Computing similarity…", "Building feedback…"];

export default function Loader() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center gap-8 py-20"
    >
      {/* Orbital spinner */}
      <div className="relative w-24 h-24">
        {/* Outer ring */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-violet-500/20"
          animate={{ rotate: 360 }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        />
        {/* Middle ring */}
        <motion.div
          className="absolute inset-2 rounded-full border-2 border-t-violet-400 border-r-transparent border-b-transparent border-l-transparent"
          animate={{ rotate: -360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        />
        {/* Inner ring */}
        <motion.div
          className="absolute inset-4 rounded-full border-2 border-t-indigo-400 border-r-indigo-400 border-b-transparent border-l-transparent"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
        />
        {/* Center dot */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="w-3 h-3 rounded-full bg-violet-500 shadow-glow-sm" />
        </motion.div>
      </div>

      {/* Cycling steps */}
      <div className="flex flex-col items-center gap-3">
        <motion.p
          className="text-slate-300 font-medium text-sm"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          Evaluating your answer
        </motion.p>
        <div className="flex flex-col gap-1.5">
          {steps.map((step, i) => (
            <motion.div
              key={step}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.4 }}
              className="flex items-center gap-2 text-xs text-slate-500"
            >
              <motion.div
                className="w-1.5 h-1.5 rounded-full bg-violet-500"
                animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.4 }}
              />
              {step}
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
