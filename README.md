# Maestro — JobForge

> A live multi-agent **AI job-application kit**. Paste a resume + a job posting and, in ~60 seconds, get a tailored resume, a cover letter, company research, and interview prep with STAR answers — produced by a **LangChain Deep Agents** orchestrator that composes spec-conformant `SKILL.md` skills into isolated subagents, visualized in real time.

Built for **The Open Accelerator — "Skilled Agents" hackathon (Lane 3: Most Innovative Use of Multiple Agents and Skills)**, June 27, 2026.

---

## ⚠️ Read this first (for the builder agent)

The entire project is specified in `docs/`. **Read them in order.** This project will be implemented by an AI coding agent (e.g. Claude Sonnet) working from these docs — they are the source of truth, written to be self-contained so you do NOT need the original planning chat.

| # | Doc | What it covers |
|---|-----|----------------|
| 00 | [`docs/00-PROJECT-BRIEF.md`](docs/00-PROJECT-BRIEF.md) | The hackathon, the rubric, the product, and **every locked decision**. Start here. |
| 01 | [`docs/01-ARCHITECTURE.md`](docs/01-ARCHITECTURE.md) | System design, data flow, the SKILL.md→subagent bridge, file tree. |
| 02 | [`docs/02-EVENT-SCHEMA.md`](docs/02-EVENT-SCHEMA.md) | **The contract** between backend and frontend. Both sides MUST match this. |
| 03 | [`docs/03-BACKEND-SPEC.md`](docs/03-BACKEND-SPEC.md) | FastAPI + SSE + deepagents orchestrator + tools. |
| 04 | [`docs/04-FRONTEND-SPEC.md`](docs/04-FRONTEND-SPEC.md) | Svelte dashboard, components, visual design, mock mode. |
| 05 | [`docs/05-SKILLS-SPEC.md`](docs/05-SKILLS-SPEC.md) | All 5 `SKILL.md` skills, frontmatter + body content. |
| 06 | [`docs/06-EVAL-AND-ADLC.md`](docs/06-EVAL-AND-ADLC.md) | Eval harness, the before/after metric, ADLC worksheet. |
| 07 | [`docs/07-BUILD-PLAN-AND-TASKS.md`](docs/07-BUILD-PLAN-AND-TASKS.md) | Decomposed tasks, build order, parallelization, acceptance criteria. |

## Locked stack (do not re-litigate)
- **Backend:** Python 3.11+, FastAPI, SSE. `deepagents` + `langchain-anthropic`.
- **Frontend:** Svelte + Vite, `EventSource` SSE client. (Pure-Python NiceGUI is the only sanctioned fallback if no JS capacity.)
- **Models:** Haiku 4.5 (extract/score) · Sonnet 4.6 (write/orchestrate).
- **Web search:** live + cached for `company-research`.
- **Skills:** all 5, validated by `skills-ref validate`.

## Definition of done (hackathon submission)
- [ ] `skills-ref validate skills/*` passes for all 5 skills.
- [ ] End-to-end live run produces all 4 deliverables + a before/after ATS score.
- [ ] Dashboard shows live orchestration (todos, subagents, score dial).
- [ ] Mock mode (`trace.json`) replays the demo with no network.
- [ ] `eval/run_eval.py` prints a before/after table over the dataset.
- [ ] Public repo, MIT `LICENSE`, this `README`, completed `ADLC.md`.
