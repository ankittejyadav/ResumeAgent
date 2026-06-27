# JobForge — Submission

**Team:** [team name / members]  ·  **Lane 3:** Most Innovative Use of Multiple Agents & Skills
**Repo:** [public URL]  ·  **License:** MIT  ·  **Demo:** [link / "see README to run"]

---

## Problem
Tailoring a job application — rewriting a resume to a posting, drafting a cover letter, researching the company, and preparing for the interview — takes most applicants 1–3 hours per role, and people apply to dozens. The work is repetitive, hard to do consistently, and offers no objective signal of whether a resume actually matches the posting.

## What we built
**JobForge** turns a resume and one or more job postings into a complete, tailored application kit in about a minute:
- **Tailored resume** — bullets rewritten and reordered to match the posting's requirements (no fabricated experience).
- **Cover letter** — specific to the role and company.
- **Company research** — mission, recent news, and culture signals from live web search.
- **Interview prep** — likely questions with STAR-format answers grounded in the candidate's actual resume.
- **ATS match score** — an objective 0–100 keyword/requirement match, reported **before and after** tailoring, with the specific keywords closed.

## How it works — multi-agent orchestration + composable skills
JobForge is built on **LangChain Deep Agents**. An **orchestrator** decomposes the task into a plan and delegates each part to a specialist **subagent that runs in isolated context**. Each subagent's expertise is defined by a portable, spec-conformant **`SKILL.md`** (per the `agentskills.io` standard) that our loader composes directly into the agent at runtime.

| Skill (`SKILL.md`) | Model | Responsibility |
|---|---|---|
| `resume-tailor` | Sonnet 4.6 | Match resume to the posting's requirements |
| `cover-letter` | Sonnet 4.6 | Draft a role- and company-specific letter |
| `company-research` | Haiku 4.5 + web search | Summarize the company from live sources |
| `interview-prep` | Sonnet 4.6 | Likely questions + STAR answers from the resume |
| `ats-scorer` | Haiku 4.5 | Independent match scorer; runs before & after tailoring |

A first pass extracts the posting into a structured requirement list and the resume into a fact list; subagents work from those shared artifacts. The independent `ats-scorer` then drives a closed loop — the tailored resume is re-scored, and missing keywords are fed back to improve the match. The scorer is deliberately separate from the writer so quality is measured by an agent that did not produce the work.

## Evaluation
We measure tailoring effectiveness as ATS match score on the original vs. tailored resume across an [N]-example dataset (`eval/run_eval.py`).

| Metric | Before | After |
|---|---|---|
| Avg. ATS match score | [xx]% | [yy]% |
| Avg. keyword coverage | [xx]% | [yy]% |

One observe→iterate cycle: [one-line summary of the change made and the resulting lift]. Full results in `eval/results.md`; process documented in `ADLC.md`.

## Model selection rationale
| Component | Model | Rationale (cost / latency / quality) |
|---|---|---|
| Orchestrator + writing skills | Sonnet 4.6 | Planning, delegation, and output quality drive value here. |
| Research, extraction, scoring | Haiku 4.5 | Mechanical/extractive work — optimized for cost and latency; scoring kept deterministic for comparable before/after numbers. |

## Stack & how to run
Python · FastAPI (SSE) · LangChain Deep Agents · Svelte + Vite frontend · Claude (Anthropic).
```
pip install -r requirements.txt && cp .env.example .env   # add ANTHROPIC_API_KEY
uvicorn server:app            # backend
cd web && npm install && npm run dev   # frontend → open the shown URL
```
All five skills validate with `skills-ref validate skills/*`. See `README.md` for full setup and `docs/` for design detail.
