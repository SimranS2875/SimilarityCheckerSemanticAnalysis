"""
report_generator.py
Generate a PDF evaluation report using fpdf2.
"""

from fpdf import FPDF
from typing import List, Dict, Any
import io
from datetime import datetime


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(15, 23, 42)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "  Automated Answer Evaluation Report", fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"Page {self.page_no()} | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")


def _score_color(pct: float):
    if pct >= 75:
        return (16, 185, 129)   # green
    elif pct >= 45:
        return (245, 158, 11)   # amber
    else:
        return (244, 63, 94)    # red


def _ai_color(pct: float):
    if pct >= 75:
        return (244, 63, 94)    # red — likely AI
    elif pct >= 50:
        return (245, 158, 11)   # amber
    else:
        return (16, 185, 129)   # green — human


def generate_report(results: List[Dict[str, Any]], student_name: str = "Student") -> bytes:
    """
    Generate a PDF report from batch evaluation results.

    Args:
        results: List of per-question evaluation dicts
        student_name: Optional student name for the report header

    Returns:
        PDF as bytes
    """
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Summary header ────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, f"Student: {student_name}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Total Questions: {len(results)}", ln=True)

    # Overall average
    avg_score_pct = sum(r["score"] / r["max_score"] * 100 for r in results) / len(results) if results else 0
    avg_ai_pct    = sum(r["ai_detection"]["ai_probability_pct"] for r in results) / len(results) if results else 0

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*_score_color(avg_score_pct))
    pdf.cell(0, 6, f"Overall Score: {avg_score_pct:.1f}%", ln=True)
    pdf.set_text_color(*_ai_color(avg_ai_pct))
    pdf.cell(0, 6, f"Average AI Probability: {avg_ai_pct:.1f}%", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # ── Divider ───────────────────────────────────────────────────────────────
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # ── Per-question sections ─────────────────────────────────────────────────
    for i, r in enumerate(results):
        score_pct = r["score"] / r["max_score"] * 100
        ai_pct    = r["ai_detection"]["ai_probability_pct"]

        # Question header
        pdf.set_fill_color(241, 245, 249)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 9, f"  Q{i+1}: {r['question'][:100]}{'...' if len(r['question']) > 100 else ''}", fill=True, ln=True)
        pdf.ln(1)

        # Score bar row
        col_w = 90
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(col_w, 6, "SCORE", ln=False)
        pdf.cell(col_w, 6, "AI DETECTION", ln=True)

        # Score value
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(*_score_color(score_pct))
        pdf.cell(col_w, 10, f"{r['score']}/{r['max_score']}  ({r['score_label']})", ln=False)

        # AI value
        pdf.set_text_color(*_ai_color(ai_pct))
        pdf.cell(col_w, 10, f"{ai_pct:.1f}%  -  {r['ai_detection']['verdict']}", ln=True)
        pdf.set_text_color(0, 0, 0)

        # Progress bars
        bar_y = pdf.get_y()
        bar_h = 4
        bar_w = 85

        # Score bar
        pdf.set_fill_color(230, 230, 230)
        pdf.rect(10, bar_y, bar_w, bar_h, "F")
        fill_w = bar_w * (score_pct / 100)
        pdf.set_fill_color(*_score_color(score_pct))
        pdf.rect(10, bar_y, fill_w, bar_h, "F")

        # AI bar
        pdf.set_fill_color(230, 230, 230)
        pdf.rect(105, bar_y, bar_w, bar_h, "F")
        ai_fill_w = bar_w * (ai_pct / 100)
        pdf.set_fill_color(*_ai_color(ai_pct))
        pdf.rect(105, bar_y, ai_fill_w, bar_h, "F")

        pdf.ln(8)

        # Metrics row
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(60, 5, f"Semantic Similarity: {r['similarity']}%", ln=False)
        pdf.cell(60, 5, f"Keyword Coverage: {r['keyword_coverage']}%", ln=False)
        pdf.cell(60, 5, f"Max Score: {r['max_score']}", ln=True)
        pdf.ln(2)

        # Feedback
        def feedback_section(title: str, items: List[str], color):
            if not items:
                return
            pdf.set_x(10)  # reset to left margin before any cell/multi_cell
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*color)
            pdf.cell(0, 5, title, ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(60, 60, 60)
            for item in items:
                # Sanitize item: replace non-latin1 chars to avoid FPDFUnicodeEncodingException
                safe_item = item.encode("latin-1", errors="replace").decode("latin-1")
                pdf.set_x(10)
                pdf.multi_cell(0, 4, f"  - {safe_item}")
            pdf.ln(1)

        feedback_section("Strengths",        r["feedback"]["strengths"],    (16, 185, 129))
        feedback_section("Missing Concepts", r["feedback"]["missing"],      (244, 63, 94))
        feedback_section("Improvements",     r["feedback"]["improvements"], (245, 158, 11))

        # AI signals detail
        if r["ai_detection"].get("signals"):
            pdf.set_x(10)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, "AI Detection Signals:", ln=True)
            pdf.set_font("Helvetica", "", 7)
            sigs = r["ai_detection"]["signals"]
            sig_text = "  " + "   |   ".join(f"{k.replace('_',' ').title()}: {v:.2f}" for k, v in sigs.items())
            pdf.set_x(10)
            pdf.multi_cell(0, 4, sig_text)

        pdf.ln(3)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    # Output as bytes
    return bytes(pdf.output())
