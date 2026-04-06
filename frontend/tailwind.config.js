/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Plus Jakarta Sans'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      colors: {
        accent: {
          50:  "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
        },
      },
      animation: {
        "fade-in":    "fadeIn 0.5s ease-out both",
        "slide-up":   "slideUp 0.5s cubic-bezier(0.16,1,0.3,1) both",
        "scale-in":   "scaleIn 0.4s cubic-bezier(0.16,1,0.3,1) both",
        "shimmer":    "shimmer 3s linear infinite",
        "glow":       "glow 3s ease-in-out infinite alternate",
        "float":      "float 8s ease-in-out infinite",
      },
      keyframes: {
        fadeIn:  { from: { opacity: "0" },                                          to: { opacity: "1" } },
        slideUp: { from: { opacity: "0", transform: "translateY(24px)" },           to: { opacity: "1", transform: "translateY(0)" } },
        scaleIn: { from: { opacity: "0", transform: "scale(0.92)" },                to: { opacity: "1", transform: "scale(1)" } },
        shimmer: { from: { backgroundPosition: "-200% 0" },                         to: { backgroundPosition: "200% 0" } },
        glow:    { from: { opacity: "0.3" },                                        to: { opacity: "0.7" } },
        float:   { "0%,100%": { transform: "translateY(0px)" },                     "50%": { transform: "translateY(-14px)" } },
      },
    },
  },
  plugins: [],
};
