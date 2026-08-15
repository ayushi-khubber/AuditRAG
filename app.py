import json
import os

from flask import Flask, jsonify, render_template

from src.config import REPORT_PATH
from src.pipeline import run_pipeline

app = Flask(__name__)


def load_or_run(force: bool = False) -> list[dict]:
    if force or not os.path.exists(REPORT_PATH):
        report = run_pipeline()
        os.makedirs(os.path.dirname(REPORT_PATH) or ".", exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    else:
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            report = json.load(f)
    return report


def summarize(report: list[dict]) -> dict:
    total = len(report)
    covered = sum(1 for r in report if r["status"] == "Covered")
    partial = sum(1 for r in report if r["status"] == "Partial")
    gap = sum(1 for r in report if r["status"] == "Gap")
    coverage_pct = round((covered / total) * 100, 1) if total else 0
    return {
        "total": total,
        "covered": covered,
        "partial": partial,
        "gap": gap,
        "coverage_pct": coverage_pct,
    }


@app.route("/")
def dashboard():
    report = load_or_run()
    functions = sorted(set(r["function"] for r in report))
    grouped = {fn: [r for r in report if r["function"] == fn] for fn in functions}
    return render_template("index.html", grouped=grouped, **summarize(report))


@app.route("/refresh")
def refresh():
    report = load_or_run(force=True)
    return jsonify({"status": "ok", "controls_analyzed": len(report), **summarize(report)})


@app.route("/api/report")
def api_report():
    return jsonify(load_or_run())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
