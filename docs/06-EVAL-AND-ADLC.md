# 06 — Eval Harness & ADLC Worksheet

These two deliverables capture **40 of the 80 rubric points** (ADLC 20 + a big chunk of Shippability/quant). Do not skip.

## The eval (quantitative before/after)

**Metric:** ATS match score (`ats_score` from `agent/tools.py`) on the **original** resume vs. the **tailored** resume, plus keyword coverage. The headline number: average score lift across the dataset.

### `eval/dataset.jsonl`
~8 examples, one JSON object per line:
```json
{"id":"swe-backend","resume":"<plain resume text>","job_posting":"<posting text>","gold_keywords":["python","fastapi","postgres","docker","ci/cd"]}
```
- Cover varied roles (SWE, data analyst, PM, marketing, designer) to show generality.
- Use synthetic/your-own resumes (no PII). Keep them short but realistic.

### `eval/run_eval.py`
```
for each example:
    before = ats_score(resume, job_posting)
    tailored = run resume-tailor on (resume, job_posting)   # via orchestrator or direct subagent call
    after = ats_score(tailored, job_posting)
    record before.value, after.value, lift, keyword_coverage
print a table + averages (avg_before, avg_after, avg_lift)
write eval/results.md (committed artifact)
```
- Make it runnable: `python eval/run_eval.py`. Print a clean table (use `tabulate` or manual formatting).
- **Cache** model/search calls so it's cheap to re-run.

### The "observe → iterate" loop (required: ≥1)
1. Run eval → record baseline avg_lift.
2. Observe a weakness (e.g. tailor under-uses exact keywords, or invents skills).
3. Make ONE change (tighten the `resume-tailor` SKILL.md, e.g. "mirror the posting's exact terminology; never add a skill not evidenced in the original").
4. Re-run eval → record improved avg_lift.
5. Record both numbers + the diff in `ADLC.md` and `eval/results.md`. **This is the graded evidence.**

## `ADLC.md` worksheet

Fill ALL phases. Template:

```markdown
# ADLC Worksheet — JobForge (Lane 3)

## 1. Scope
Problem, target user, success definition, non-goals.

## 2. Design
Architecture summary (link docs/01). Why multi-agent + skill composition.
The 5 skills and their boundaries.

## 3. Model selection  ← MANDATORY, graded
| Component | Model | Why (cost / latency / quality) |
|---|---|---|
| Orchestrator | Sonnet 4.6 | Needs reliable planning + tool/delegation reasoning; mid cost. |
| resume-tailor / cover-letter / interview-prep | Sonnet 4.6 | Quality of generated writing matters most here. |
| company-research | Haiku 4.5 | Summarizing search results is easy; optimize latency + cost. |
| ats-scorer | Haiku 4.5 (or deterministic) | Mechanical extraction/matching; cheapest + fastest; determinism aids eval. |

## 4. Build
What was built, the SKILL.md→subagent bridge, deviations from plan.

## 5. Evaluate / Observe  ← MANDATORY loop
Metric, dataset, baseline numbers, the one change made, post-change numbers, conclusion.
(Paste the eval table.)

## 6. Iterate
What you'd do next with more time (parallelism, more skills, PDF export, ATS synonym DB).
```

## Acceptance
- `python eval/run_eval.py` prints before/after table + averages and writes `eval/results.md`.
- `ADLC.md` complete, with the model-selection table and a real before→after number from the iterate loop.
