"""
generate_sample_pdfs.py
Generates two sample PDFs for testing the EvalAI PDF upload feature:
  - sample_model_answers.pdf   (reference/ideal answers)
  - sample_student_answers.pdf (student answers — mix of good, partial, weak)

Run: python scripts/generate_sample_pdfs.py
Output: data/sample_model_answers.pdf, data/sample_student_answers.pdf
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fpdf import FPDF

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)


# ── Q&A content ───────────────────────────────────────────────────────────────

QA = [
    {
        "question": "What is machine learning?",
        "model": (
            "Machine learning is a subset of artificial intelligence that enables systems "
            "to learn and improve from experience without being explicitly programmed. "
            "It focuses on developing algorithms that can access data and use it to learn "
            "for themselves, identifying patterns and making decisions with minimal human intervention."
        ),
        "student": (
            "Machine learning is a branch of AI where computers are trained to learn "
            "patterns from data and make decisions without being directly programmed for "
            "each task. It uses algorithms that improve automatically through experience."
        ),
        # Quality: Good paraphrase — should score ~7-8/10
    },
    {
        "question": "Explain the concept of photosynthesis.",
        "model": (
            "Photosynthesis is the process by which green plants and some other organisms "
            "use sunlight to synthesize nutrients from carbon dioxide and water. "
            "It involves the conversion of light energy into chemical energy stored in glucose, "
            "releasing oxygen as a byproduct. The process occurs in the chloroplasts of plant cells."
        ),
        "student": (
            "Photosynthesis is how plants make food using sunlight and water. "
            "Oxygen is released in the process."
        ),
        # Quality: Partial — missing carbon dioxide, glucose, chloroplasts — should score ~4-5/10
    },
    {
        "question": "What is Newton's second law of motion?",
        "model": (
            "Newton's second law of motion states that the acceleration of an object is "
            "directly proportional to the net force acting on it and inversely proportional "
            "to its mass. This relationship is expressed mathematically as F = ma, where F "
            "is the net force in Newtons, m is the mass in kilograms, and a is the acceleration "
            "in metres per second squared."
        ),
        "student": (
            "Newton's second law states that force equals mass times acceleration, written as F = ma. "
            "If you apply a greater force to an object, it accelerates more. "
            "A heavier object requires more force to achieve the same acceleration as a lighter one. "
            "The unit of force is the Newton."
        ),
        # Quality: Good — covers all key points — should score ~8/10
    },
    {
        "question": "Describe the water cycle.",
        "model": (
            "The water cycle, also known as the hydrological cycle, describes the continuous "
            "movement of water on, above, and below the surface of the Earth. "
            "Key processes include evaporation, where water from oceans and lakes turns to vapour; "
            "condensation, where vapour forms clouds; precipitation, where water falls as rain or snow; "
            "and collection, where water gathers in rivers, lakes, and groundwater reserves."
        ),
        "student": (
            "I am not sure about this topic. The water cycle involves rain and clouds. "
            "Water falls from the sky and then evaporates again."
        ),
        # Quality: Weak — very vague, missing most concepts — should score ~2-3/10
    },
    {
        "question": "What is the role of DNA in living organisms?",
        "model": (
            "DNA, or deoxyribonucleic acid, is the hereditary material found in the nucleus "
            "of cells in humans and almost all other organisms. It carries the genetic instructions "
            "for the development, functioning, growth, and reproduction of all known living organisms. "
            "DNA is organised into structures called chromosomes, and segments of DNA that encode "
            "proteins are called genes."
        ),
        "student": (
            "DNA stands for deoxyribonucleic acid and is found inside the nucleus of cells. "
            "It contains the genetic information that determines how an organism develops and functions. "
            "DNA is organised into chromosomes, and specific sections called genes encode proteins "
            "that carry out biological processes. It is passed from parents to offspring during reproduction."
        ),
        # Quality: Excellent — comprehensive, well-structured — should score ~9/10
    },
]


# ── PDF builder ───────────────────────────────────────────────────────────────

def build_pdf(title: str, qa_list: list, key: str, filename: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Header
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 14, f"  {title}", fill=True, ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    for i, item in enumerate(qa_list, start=1):
        # Question
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 9, f"  Q{i}: {item['question']}", fill=True, ln=True)
        pdf.ln(2)

        # Answer label
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(100, 100, 100)
        label = "Model Answer:" if key == "model" else "Student Answer:"
        pdf.cell(0, 6, label, ln=True)

        # Answer body
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        # Sanitize to latin-1 for Helvetica
        safe_text = item[key].encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, f"A{i}: {safe_text}")
        pdf.ln(5)

        # Divider
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    out_path = os.path.join(OUT_DIR, filename)
    pdf.output(out_path)
    print(f"  Saved: {out_path}")
    return out_path


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nGenerating sample PDFs...\n")

    build_pdf(
        title="Model Answer Sheet - EvalAI Sample",
        qa_list=QA,
        key="model",
        filename="sample_model_answers.pdf",
    )

    build_pdf(
        title="Student Answer Sheet - EvalAI Sample",
        qa_list=QA,
        key="student",
        filename="sample_student_answers.pdf",
    )

    print("\nDone! Upload these two files to the PDF Upload tab in EvalAI.")
    print("Expected score range per question:")
    print("  Q1 (Machine learning)  — ~7-8/10  (good paraphrase)")
    print("  Q2 (Photosynthesis)    — ~4-5/10  (partial answer)")
    print("  Q3 (Newton's 2nd law)  — ~8/10    (good coverage)")
    print("  Q4 (Water cycle)       — ~2-3/10  (weak/vague)")
    print("  Q5 (DNA)               — ~9/10    (excellent)")
