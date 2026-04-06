import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Lightbulb } from "lucide-react";

interface Props {
  strengths: string[];
  missing: string[];
  improvements: string[];
}

const sections = [
  {
    key: "strengths" as const,
    title: "Strengths",
    icon: CheckCircle2,
    gradient: "from-emerald-500/10 to-teal-500/5",
    border: "border-emerald-500/20",
    iconColor: "text-emerald-400",
    dotColor: "bg-emerald-400",
    textColor: "text-emerald-100",
    badge: "bg-emerald-500/15 text-emerald-300 border-emerald-500/20",
  },
  {
    key: "missing" as const,
    title: "Missing Concepts",
    icon: XCircle,
    gradient: "from-rose-500/10 to-pink-500/5",
    border: "border-rose-500/20",
    iconColor: "text-rose-400",
    dotColor: "bg-rose-400",
    textColor: "text-rose-100",
    badge: "bg-rose-500/15 text-rose-300 border-rose-500/20",
  },
  {
    key: "improvements" as const,
    title: "Improvements",
    icon: Lightbulb,
    gradient: "from-amber-500/10 to-orange-500/5",
    border: "border-amber-500/20",
    iconColor: "text-amber-400",
    dotColor: "bg-amber-400",
    textColor: "text-amber-100",
    badge: "bg-amber-500/15 text-amber-300 border-amber-500/20",
  },
];

export default function FeedbackList({ strengths, missing, improvements }: Props) {
  const data = { strengths, missing, improvements };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {sections.map((s, si) => {
        const items = data[s.key];
        const Icon = s.icon;
        return (
          <motion.div
            key={s.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: si * 0.1, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className={`relative overflow-hidden rounded-2xl border ${s.border} bg-gradient-to-br ${s.gradient} p-5 flex flex-col gap-4`}
          >
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${s.badge} border`}>
                  <Icon size={13} />
                </div>
                <span className="text-xs font-bold uppercase tracking-widest text-slate-400">{s.title}</span>
              </div>
              <span className={`tag ${s.badge} font-mono font-bold`}>{items.length}</span>
            </div>

            {/* Items */}
            {items.length === 0 ? (
              <p className="text-xs text-slate-600 italic">Nothing to report</p>
            ) : (
              <ul className="flex flex-col gap-2.5">
                {items.map((item, i) => (
                  <motion.li
                    key={i}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: si * 0.1 + i * 0.06 }}
                    className={`flex gap-2.5 text-sm leading-relaxed ${s.textColor}`}
                  >
                    <span className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${s.dotColor}`} />
                    <span className="opacity-90">{item}</span>
                  </motion.li>
                ))}
              </ul>
            )}

            {/* Decorative corner glow */}
            <div className={`absolute -bottom-6 -right-6 w-20 h-20 rounded-full blur-2xl opacity-20 ${s.dotColor}`} />
          </motion.div>
        );
      })}
    </div>
  );
}
