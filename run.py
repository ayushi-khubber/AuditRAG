import argparse
import json

from src.config import REPORT_PATH
from src.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Run the AuditRAG gap analysis pipeline.")
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip Llama 3.3 70B narrative generation (faster, no GROQ_API_KEY needed).",
    )
    parser.add_argument(
        "--output", default=REPORT_PATH, help=f"Where to write the JSON report (default: {REPORT_PATH})"
    )
    args = parser.parse_args()

    report = run_pipeline(generate_narratives=not args.skip_llm)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    total = len(report)
    covered = sum(1 for r in report if r["status"] == "Covered")
    partial = sum(1 for r in report if r["status"] == "Partial")
    gap = sum(1 for r in report if r["status"] == "Gap")
    coverage_pct = round((covered / total) * 100, 1) if total else 0

    print("\n--- Summary ---")
    print(f"Total controls analyzed: {total}")
    print(f"Covered: {covered}  Partial: {partial}  Gap: {gap}")
    print(f"Full coverage: {coverage_pct}%")
    print(f"Report written to: {args.output}")


if __name__ == "__main__":
    main()
