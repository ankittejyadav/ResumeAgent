# JobForge — One-Pager

**What:** A multi-agent AI job-application kit. Paste a resume + job posting(s) → tailored resume, cover letter, company research, and interview prep (STAR answers), with a **before/after ATS match score**.

**Event:** The Open Accelerator "Skilled Agents" hackathon — **Lane 3: Most Innovative Use of Multiple Agents & Skills**. June 27, 2026. 6-hour build. Teams ≤5.

**Why it exists:** Saves real time (tailoring an app takes 1–3 hrs; this is ~1 min), feasible (text in/out — no OAuth/DB), real users (job-seekers in the room).

---

## Architecture
- **Agents:** LangChain **Deep Agents** (`deepagents`, Python) — orchestrator plans via `write_todos`, delegates to specialist subagents with isolated context.
- **The novelty / bridge:** each skill is a spec-conformant **`SKILL.md`** loaded into a Deep Agents subagent (body → system prompt, frontmatter `description` → delegation routing).
- **Backend:** Python + FastAPI, **SSE** event stream.
- **Frontend:** Svelte + Vite, `EventSource` client. **Mock mode** replays `trace.json` offline (demo safety net).
- **Models:** Haiku 4.5 (extract/score/research) · Sonnet 4.6 (write/orchestrate).
- **Web search:** live (Tavily/DuckDuckGo) + disk cache.

## The 5 skills (one SKILL.md each → one subagent)
| Skill | Model | Role |
|---|---|---|
| `resume-tailor` | Sonnet | Rewrite bullets to match JD keywords (no fabrication) |
| `cover-letter` | Sonnet | Tailored letter using research |
| `company-research` | Haiku + web | Mission, news, culture from live search |
| `interview-prep` | Sonnet | Likely Qs + STAR answers grounded in resume |
| `ats-scorer` | Haiku / deterministic | 0–100 match %, matched/missing keywords. **Independent checker, runs before & after.** |

## Run flow (true parallel DAG — for speed)
`extract ∥ company-research ∥ score-before` → `resume-tailor` + `interview-prep` (parallel) → `cover-letter` (needs tailor+research) → `score-after` → assemble.

---

## Product principles (what makes it actually worth using, not a demo wrapper)
1. **Extract once:** a cheap Haiku pass turns JD→requirement list and resume→fact list; pass those compact artifacts to subagents (not raw text 5×). Cuts tokens + improves quality.
2. **Closed loop:** tailor consumes the scorer's *missing keywords* and re-tailors to close the gap → measurably better than a one-shot prompt.
3. **Batch mode:** one resume × several JDs → ranked match-score table + a kit per job. This is where multi-agent beats "just do it yourself."
4. **Output-first UX:** stream editable deliverables as they complete; first useful content <10s. Agent-graph viz is garnish, not the main event. Everything inline-editable.

## Scoring (80 pts) — where our points come from
Shippability/spec (25): runs + `skills-ref validate` passes + public repo + MIT + README · ADLC (20): worksheet + **before/after ATS eval loop** · Lane merit (20): orchestration novelty · Skill quality (15): grounded expertise + gotchas + output templates per SKILL.md.

## Must-haves for submission
- [ ] `skills-ref validate skills/*` passes (all 5)
- [ ] Live end-to-end run: 4 deliverables + before/after score
- [ ] Mock mode works offline (`trace.json`)
- [ ] `python eval/run_eval.py` → before/after table + averages
- [ ] `ADLC.md` complete incl. **model-selection rationale** (cost/latency/quality)
- [ ] Public repo, MIT `LICENSE`, `README.md`

## Key risks → mitigations
deepagents API differs → verify docs early + explicit-orchestration fallback · wifi/API dies → mock mode · token waste → extract-once + cache · multi-agent slower than 1 prompt for a *single* job → justified only by batch mode + closed loop + parallel latency.

**Full specs:** see `README.md` → `docs/00`–`07`.
