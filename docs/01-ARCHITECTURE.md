# 01 — Architecture

## System diagram
```
   ┌─────────────────────────────┐         SSE (text/event-stream)
   │  Svelte UI (web/, Vite)     │ ◄───────────────────────────────┐
   │  EventSource → eventStore   │                                  │
   │  panels: Todos, Agent graph,│         POST /run {resume,job}   │
   │  Skill shelf, Score dial,   │ ────────────────────────────────┼──► FastAPI
   │  Deliverables, Activity log │                                  │   (server.py)
   └─────────────────────────────┘                                  │
                                                                     │
   FastAPI (server.py)                                               │
   ├─ POST /run        → starts a run, returns run_id                │
   ├─ GET  /events/{id}→ SSE stream of events ──────────────────────┘
   ├─ GET  /mock       → replays trace.json over SSE (demo safety)
   └─ event bus: asyncio.Queue per run_id
                       ▲ pushes typed events (see 02-EVENT-SCHEMA.md)
                       │
   agent/orchestrator.py
   ├─ build_agent(skills) → deepagents create_deep_agent(
   │      model=Sonnet, tools=[web_search, ats_score],
   │      subagents=[<one per SKILL.md>])
   ├─ run(resume, job, emit) → astream_events loop → emit(event)
   │
   ├─ agent/skill_loader.py : SKILL.md → subagent dict (THE BRIDGE)
   └─ agent/tools.py        : web_search (live+cache), ats_score()

   skills/<name>/SKILL.md  ×5   (validated by skills-ref)
```

## Request/run lifecycle
1. UI `POST /run` with `{resume, job_posting}` → server creates `run_id`, an `asyncio.Queue`, kicks off the orchestrator task, returns `{run_id}`.
2. UI opens `EventSource("/events/{run_id}")`.
3. Orchestrator streams events as it works; server relays each onto the queue → SSE.
4. On completion server emits a `done` event and closes the stream.

> Single-user demo: in-memory `dict[run_id] → Queue` is fine. No DB. No auth.

## The SKILL.md → subagent bridge (our core novelty)
`skill_loader.load_skills(dir="skills/")` returns a list of subagent definitions:
```python
# pseudocode — verify exact deepagents subagent schema against docs
{
  "name": frontmatter["name"],               # e.g. "resume-tailor"
  "description": frontmatter["description"],  # used by orchestrator to decide delegation
  "prompt": markdown_body,                    # the skill instructions = subagent system prompt
  "model": MODEL_FOR_SKILL[name],             # Haiku or Sonnet per 00-brief table
  "tools": TOOLS_FOR_SKILL.get(name, []),     # e.g. company-research gets web_search
}
```
- Parse frontmatter with `python-frontmatter` or `yaml` + manual split on `---`.
- The orchestrator's `system_prompt` tells it: plan with `write_todos`, then delegate each part to the best-matching subagent by description, run `ats_score` before and after, and assemble the final kit.
- **Emit a `skill_loaded` event per skill at startup** so the UI's skill shelf populates.

## Orchestration flow (the actual run)
```
1. emit run_started
2. orchestrator: write_todos([research, score-before, tailor, cover, interview, score-after, assemble])
   → emit plan + todo_update events
3. ats_score(original_resume, job) → emit score_update {phase:"before", value}
4. delegate (parallel where possible):
     company-research → emit subagent_start/finish + deliverable(company)
     resume-tailor    → emit subagent_start/finish + deliverable(resume)
     cover-letter     → emit ... + deliverable(cover_letter)
     interview-prep   → emit ... + deliverable(interview)
5. ats_score(tailored_resume, job) → emit score_update {phase:"after", value}
6. emit done {summary, before, after, deliverables}
```
> Parallelism note: Deep Agents drives delegation via the model. If true parallel tool calls aren't reliably emitted, sequential delegation is acceptable for the MVP — the UI still animates per-subagent. Don't block the build on perfect parallelism.

## File tree (target)
```
maestro/
├── README.md
├── LICENSE                      # MIT
├── ADLC.md                      # the worksheet (see 06)
├── trace.json                   # recorded run for mock mode
├── .env.example                 # ANTHROPIC_API_KEY, TAVILY_API_KEY
├── requirements.txt
├── server.py                    # FastAPI + SSE + event bus
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py          # build_agent + run loop (astream_events→emit)
│   ├── skill_loader.py          # SKILL.md → subagent (the bridge)
│   ├── tools.py                 # web_search (live+cache), ats_score
│   └── events.py                # event constructors / schema helpers
├── skills/
│   ├── resume-tailor/SKILL.md
│   ├── cover-letter/SKILL.md
│   ├── company-research/SKILL.md
│   ├── interview-prep/SKILL.md
│   └── ats-scorer/SKILL.md
├── eval/
│   ├── dataset.jsonl            # ~8 (resume, job, gold_keywords)
│   └── run_eval.py              # before/after ATS table
└── web/                         # Svelte + Vite
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.svelte
        ├── lib/eventStore.js    # SSE client + state
        └── components/
            ├── ScoreDial.svelte
            ├── TodoPanel.svelte
            ├── AgentGraph.svelte
            ├── SkillShelf.svelte
            ├── Deliverables.svelte
            └── ActivityLog.svelte
```

## Cross-cutting concerns
- **CORS:** Vite dev server (`http://localhost:5173`) ≠ FastAPI (`http://localhost:8000`). Add `CORSMiddleware` allowing the dev origin. For the demo you may also build the Svelte app and serve `web/dist` as static files from FastAPI to avoid CORS entirely (preferred for a single-process booth setup).
- **Determinism/cost:** cache web-search results to disk (`.cache/`) keyed by query. Set low temperature on scoring.
- **Secrets:** `.env` (gitignored), `.env.example` committed. Never commit keys.
- **Failure handling:** every subagent wrapped so a failure emits `subagent_error` and the run continues with partial deliverables.
