# 03 — Backend Spec (Python + FastAPI + deepagents)

## Dependencies (`requirements.txt`)
```
fastapi
uvicorn[standard]
deepagents
langchain-anthropic
python-frontmatter
python-dotenv
tavily-python        # or duckduckgo-search if no Tavily key
pydantic
```
> Verify `deepagents` import surface against https://docs.langchain.com/oss/python/deepagents/overview before coding — the create function and subagent schema are the only API-shape risks in this project.

## Environment (`.env`)
```
ANTHROPIC_API_KEY=...
TAVILY_API_KEY=...           # optional; fall back to duckduckgo-search if absent
MAESTRO_OFFLINE=0            # 1 = skip live search, use cache/stub (demo safety)
```

## `server.py`
- FastAPI app + `CORSMiddleware` (allow `http://localhost:5173`).
- `runs: dict[str, asyncio.Queue]` in-memory.
- Endpoints:
  - `POST /run` body `{resume: str, job_posting: str}` → create `run_id` (uuid), create queue, `asyncio.create_task(orchestrate(...))`, return `{"run_id": id}`.
  - `GET /events/{run_id}` → `StreamingResponse(gen(), media_type="text/event-stream")`. `gen()` awaits queue items, yields `sse(event)`, breaks after `done`.
  - `GET /mock` → reads `trace.json`, streams events honoring `delay_ms` (use `asyncio.sleep`).
  - (Optional) mount `web/dist` as static files at `/` for single-process demo.
- Headers for SSE: `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no`.

```python
@app.post("/run")
async def run(body: RunIn):
    rid = uuid4().hex
    q = asyncio.Queue(); runs[rid] = q
    async def emit(evt): await q.put(evt)
    asyncio.create_task(orchestrate(body.resume, body.job_posting, emit))
    return {"run_id": rid}

@app.get("/events/{rid}")
async def events(rid: str):
    q = runs[rid]
    async def gen():
        while True:
            evt = await q.get()
            yield sse(evt)
            if evt["type"] == "done": break
    return StreamingResponse(gen(), media_type="text/event-stream", headers=SSE_HEADERS)
```

## `agent/skill_loader.py`
```python
import frontmatter, pathlib
MODEL_FOR_SKILL = {
  "resume-tailor":"claude-sonnet-4-6","cover-letter":"claude-sonnet-4-6",
  "interview-prep":"claude-sonnet-4-6","company-research":"claude-haiku-4-5-20251001",
  "ats-scorer":"claude-haiku-4-5-20251001",
}
def load_skills(root="skills"):
    out=[]
    for p in sorted(pathlib.Path(root).glob("*/SKILL.md")):
        post = frontmatter.load(p)
        name = post["name"]; desc = post["description"]
        out.append({"name":name,"description":desc,"prompt":post.content,
                    "model":MODEL_FOR_SKILL.get(name,"claude-sonnet-4-6"),
                    "tools": ["web_search"] if name=="company-research" else []})
    return out
```

## `agent/tools.py`
- `ats_score(resume: str, job_posting: str) -> dict` — deterministic-ish keyword/requirement match. Implementation: extract required skills/keywords from `job_posting` (can be a Haiku call OR a simple keyword set), compute % present in `resume`, return `{value, matched_keywords, missing_keywords}`. Keep it cheap and explainable; the UI needs `missing_keywords`. **This is also imported by `eval/run_eval.py` — keep it pure/importable.**
- `web_search(query: str) -> str` — Tavily (or duckduckgo-search) with a disk cache in `.cache/` keyed by query hash. Respect `MAESTRO_OFFLINE`. Return a compact text summary (cap length).

## `agent/orchestrator.py`
- `build_agent()`:
  ```python
  from deepagents import create_deep_agent   # VERIFY exact name
  subagents = load_skills()
  agent = create_deep_agent(
      model="claude-sonnet-4-6",
      tools=[web_search, ats_score],
      system_prompt=ORCH_PROMPT,
      subagents=subagents,        # VERIFY key name (subagents=?)
  )
  ```
- `ORCH_PROMPT` (the orchestrator's brain): instruct it to (1) call `write_todos` with the 7-step plan, (2) score the original resume first via `ats_score`, (3) delegate to `company-research`, `resume-tailor`, `cover-letter`, `interview-prep`, (4) re-score the tailored resume, (5) return a structured final result. Tell it to keep deliverables in Markdown.
- `orchestrate(resume, job, emit)`:
  - emit `run_started`, then `skill_loaded` for each loaded skill.
  - run `agent.astream_events(...)` (verify method) and **map LangGraph events → our schema** (02). Key mappings:
    - tool start `write_todos` → `plan` / `todo_update`
    - subagent/tool invocation start/end → `subagent_start`/`subagent_finish`
    - `ats_score` tool result → `score_update`
    - final messages with deliverable content → `deliverable`
    - token usage from `on_chat_model_end` metadata → `token_usage`
  - Wrap in try/except → `subagent_error` / `log(error)`.
  - Always emit `done` at the end.

> If `astream_events` mapping proves fiddly under time pressure, the **fallback** is to NOT use full autonomy: orchestrate the steps explicitly in Python (call each subagent/tool in sequence yourself) and emit events directly. This guarantees clean events and a reliable demo. Document whichever path you choose in `ADLC.md`. The multi-agent + skill-composition story holds either way.

## Acceptance (backend)
- `uvicorn server:app` boots; `POST /run` + `GET /events/{id}` produce a full event sequence ending in `done`.
- `GET /mock` replays `trace.json`.
- All 5 skills load and emit `skill_loaded`.
