"""
eval/run_eval.py — before/after ATS score evaluation.

Run: python eval/run_eval.py

For each example in dataset.jsonl:
  1. Score original resume (before)
  2. Call resume-tailor subagent to produce a tailored resume
  3. Score tailored resume (after)
  4. Compute lift

Prints a table and writes eval/results.md.
"""
import json
import os
import sys
import pathlib

# Add project root to path so we can import agent/
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from agent.tools import ats_score
from agent.skill_loader import load_skills

try:
    import anthropic
    _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
except Exception:
    _client = None

try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False

DATASET = pathlib.Path(__file__).parent / "dataset.jsonl"
RESULTS_MD = pathlib.Path(__file__).parent / "results.md"

SONNET = "claude-sonnet-4-6"


def load_dataset():
    with open(DATASET) as f:
        return [json.loads(line) for line in f if line.strip()]


def tailor_resume(resume: str, job_posting: str, skill_prompt: str) -> str:
    """Call the resume-tailor skill via Anthropic API."""
    if _client is None:
        return resume  # no-op if no API key

    msg = _client.messages.create(
        model=SONNET,
        max_tokens=2048,
        system=skill_prompt,
        messages=[
            {"role": "user", "content": f"Resume:\n{resume}\n\nJob Posting:\n{job_posting}\n\nProduce the tailored resume."}
        ],
    )
    return msg.content[0].text


def run_eval():
    print("JobForge — ATS Score Eval\n" + "=" * 50)
    examples = load_dataset()
    skills = load_skills()
    skill_map = {s["name"]: s for s in skills}
    rt_prompt = skill_map.get("resume-tailor", {}).get("prompt", "Tailor the resume to the job posting.")

    rows = []
    for ex in examples:
        eid = ex["id"]
        resume = ex["resume"]
        job = ex["job_posting"]
        gold = ex.get("gold_keywords", [])

        before = ats_score(resume, job)

        if _client:
            tailored = tailor_resume(resume, job, rt_prompt)
        else:
            tailored = resume
            print(f"  [{eid}] No ANTHROPIC_API_KEY — using original resume as tailored.")

        after = ats_score(tailored, job)
        lift = after["value"] - before["value"]
        gold_coverage = round(
            len([k for k in gold if k.lower() in tailored.lower()]) / len(gold) * 100
        ) if gold else 0

        rows.append({
            "id": eid,
            "before": before["value"],
            "after": after["value"],
            "lift": lift,
            "gold_coverage": gold_coverage,
            "missing_before": len(before["missing_keywords"]),
            "missing_after": len(after["missing_keywords"]),
        })
        print(f"  {eid:20s} | before={before['value']:3d}%  after={after['value']:3d}%  lift={lift:+4d}  gold={gold_coverage}%")

    avg_before = round(sum(r["before"] for r in rows) / len(rows))
    avg_after = round(sum(r["after"] for r in rows) / len(rows))
    avg_lift = round(sum(r["lift"] for r in rows) / len(rows))
    avg_gold = round(sum(r["gold_coverage"] for r in rows) / len(rows))

    print("\n" + "-" * 50)
    print(f"  {'AVERAGE':20s} | before={avg_before:3d}%  after={avg_after:3d}%  lift={avg_lift:+4d}  gold={avg_gold}%")
    print()

    if _HAS_TABULATE:
        table_data = [[r["id"], r["before"], r["after"], f"{r['lift']:+d}", r["gold_coverage"]] for r in rows]
        table_data.append(["**AVERAGE**", avg_before, avg_after, f"{avg_lift:+d}", avg_gold])
        print(tabulate(table_data, headers=["ID", "Before %", "After %", "Lift", "Gold Coverage %"], tablefmt="github"))

    write_results_md(rows, avg_before, avg_after, avg_lift, avg_gold)
    print(f"\nResults written to {RESULTS_MD}")
    return {"avg_before": avg_before, "avg_after": avg_after, "avg_lift": avg_lift}


def write_results_md(rows, avg_before, avg_after, avg_lift, avg_gold):
    lines = [
        "# Eval Results — JobForge ATS Score\n",
        "## Summary\n",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Average Before | {avg_before}% |",
        f"| Average After | {avg_after}% |",
        f"| Average Lift | +{avg_lift} pts |",
        f"| Avg Gold Keyword Coverage | {avg_gold}% |",
        "",
        "## Per-example results\n",
        "| ID | Before | After | Lift | Gold Coverage |",
        "|----|--------|-------|------|---------------|",
    ]
    for r in rows:
        lines.append(f"| {r['id']} | {r['before']}% | {r['after']}% | {r['lift']:+d} | {r['gold_coverage']}% |")
    lines += [
        f"| **AVERAGE** | **{avg_before}%** | **{avg_after}%** | **+{avg_lift}** | **{avg_gold}%** |",
        "",
        "## Notes",
        "- `ats_score` in `agent/tools.py` is the authoritative scorer (deterministic keyword/synonym matching).",
        "- Tailoring via `resume-tailor` skill (Sonnet 4.6 model).",
        "- See ADLC.md for the observe→iterate loop and model selection rationale.",
    ]
    RESULTS_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run_eval()
