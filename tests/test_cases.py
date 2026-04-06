"""
test_cases.py
Automated test runner for all test cases.
Saves results to results/outputs.json and results/evaluation_metrics.csv
Run: python tests/test_cases.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import csv
import math
from src.evaluator import evaluate

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
TEST_CASES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "test_cases.json")


def run_all_tests() -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open(TEST_CASES_PATH, "r") as f:
        test_cases = json.load(f)

    outputs = []
    metrics_rows = []

    print(f"\n{'='*60}")
    print("  AUTOMATED ANSWER EVALUATION — TEST SUITE")
    print(f"{'='*60}\n")

    for tc in test_cases:
        print(f"Running {tc['id']} [{tc['type']}]...")
        result = evaluate(
            question=tc["question"],
            model_answer=tc["model_answer"],
            student_answer=tc["student_answer"],
        )

        predicted = result["score"]
        human = tc.get("human_score", None)
        expected_min = tc.get("expected_score_min", 0)

        passed = predicted >= expected_min
        status = "PASS" if passed else "FAIL"

        print(f"  Score: {predicted}/10  |  Human: {human}  |  Status: {status}")
        print(f"  Semantic: {result['semantic_similarity_pct']}%  |  Keywords: {result['keyword_coverage_pct']}%")
        print(f"  Label: {result['score_label']}")
        print()

        outputs.append({
            "id": tc["id"],
            "type": tc["type"],
            "question": tc["question"],
            "predicted_score": predicted,
            "human_score": human,
            "expected_score_min": expected_min,
            "status": status,
            "semantic_similarity_pct": result["semantic_similarity_pct"],
            "keyword_coverage_pct": result["keyword_coverage_pct"],
            "score_label": result["score_label"],
            "strengths": result["strengths"],
            "missing_concepts": result["missing_concepts"],
            "improvements": result["improvements"],
        })

        if human is not None:
            mae = abs(predicted - human)
            metrics_rows.append({
                "id": tc["id"],
                "type": tc["type"],
                "predicted_score": predicted,
                "human_score": human,
                "absolute_error": round(mae, 2),
                "semantic_similarity": result["semantic_similarity_pct"] / 100,
                "keyword_coverage": result["keyword_coverage_pct"] / 100,
            })

    # Save outputs.json
    out_path = os.path.join(RESULTS_DIR, "outputs.json")
    with open(out_path, "w") as f:
        json.dump(outputs, f, indent=2)
    print(f"Results saved to {out_path}")

    # Save evaluation_metrics.csv
    csv_path = os.path.join(RESULTS_DIR, "evaluation_metrics.csv")
    if metrics_rows:
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=metrics_rows[0].keys())
            writer.writeheader()
            writer.writerows(metrics_rows)

        mae_values = [r["absolute_error"] for r in metrics_rows]
        mean_mae = round(sum(mae_values) / len(mae_values), 3)
        print(f"Metrics saved to {csv_path}")
        print(f"\nMean Absolute Error (vs human scores): {mean_mae}")

    passed_count = sum(1 for o in outputs if o["status"] == "PASS")
    print(f"\nTest Results: {passed_count}/{len(outputs)} passed")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_all_tests()
