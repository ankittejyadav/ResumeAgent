# 07 — Build Plan & Task Breakdown (for builder agents)

Decomposed so multiple agents (or a team) can work in parallel. The **event schema (02)** is the contract that lets backend and frontend proceed independently — agree on it first, then fan out.

## Build order & dependencies
```
T0 Scaffold ──┬─► T1 Skills (5×SKILL.md) ──► validate
              ├─► T2 Backend (loader, tools, orchestrator, server) ──┐
              ├─► T3 Frontend (Svelte, store, components) ───────────┤
              │      (T2 & T3 parallel — both code only to schema 02)│
              ├─► T4 Eval + ADLC (needs tools.ats_score from T2) ────┤
              └────────────────────────────────────────► T5 Integrate (live run)
                                                          └─► T6 Record trace.json (mock) ─► T7 Polish/Docs
```

## Tasks

### T0 — Scaffold (foundation; do first)
- Create file tree (01). `requirements.txt`, `.env.example`, `.gitignore` (`.env`, `.cache/`, `node_modules/`, `dist/`, `__pycache__/`).
- `git init`, MIT `LICENSE`, commit. **Tag baseline.**
- **AC:** repo builds an empty venv; `pip install -r requirements.txt` succeeds; `npm create vite` done in `web/`.

### T1 — Skills (assignable solo)
- Write all 5 `SKILL.md` per `05-SKILLS-SPEC.md`. Folder name == frontmatter `name`.
- **AC:** `skills-ref validate skills/*` passes for all 5.

### T2 — Backend (assignable solo; codes to schema 02)
- `agent/skill_loader.py`, `agent/tools.py` (`ats_score`, `web_search`+cache), `agent/events.py`, `agent/orchestrator.py`, `server.py`.
- **First milestone:** terminal run of the orchestrator on a sample (resume, job) printing events to stdout — before touching SSE.
- **VERIFY deepagents API** (`create_deep_agent` signature, `subagents=` key, `astream_events`) against docs before deep coding. If autonomy mapping is fiddly, use the explicit-orchestration fallback (see 03).
- **AC:** `POST /run` → `GET /events/{id}` yields a full schema-valid sequence ending in `done`; `/mock` works; 5 `skill_loaded` events emitted.

### T3 — Frontend (assignable solo; codes to schema 02)
- Vite+Svelte app, `lib/eventStore.js`, all components (04). Build against a **local mock `trace.json`** first so it needs no backend.
- **AC:** dashboard animates from events; score dial climbs; deliverables render+copy; mock toggle works offline.

### T4 — Eval + ADLC (assignable solo; needs `tools.ats_score`)
- `eval/dataset.jsonl` (~8), `eval/run_eval.py`, run the observe→iterate loop, write `eval/results.md` + `ADLC.md` (06).
- **AC:** `python eval/run_eval.py` prints before/after averages; ADLC complete with model-selection table + a real lift number.

### T5 — Integrate (after T2+T3 green)
- Point Svelte at FastAPI (CORS or serve `web/dist` from FastAPI). Run a real end-to-end forge.
- Fix schema mismatches **by updating 02 first**, then both sides.
- **AC:** one paste→Forge→full kit live run works on the demo machine.

### T6 — Record mock trace
- Capture the events of one good live run into `trace.json` (add `delay_ms`). This is the stage safety net.
- **AC:** mock mode reproduces that run with network OFF.

### T7 — Polish & docs
- Visual pass (score-dial hero animation, spacing, mode badge). README final. Sample resume/job seeded in the input screen. Dry-run the 2-minute demo.
- **AC:** README definition-of-done checklist all ticked.

## Time-boxing (≈6h, team ~5)
| Block | Focus |
|---|---|
| 0:00–0:30 | T0 scaffold + baseline tag + agree on schema 02 |
| 0:30–2:00 | T1 skills · T2 backend-to-terminal · T3 UI-from-mock (parallel) |
| 2:00–3:15 | T2 SSE + T3 components done · T4 eval starts |
| 3:15–4:15 | T5 integrate live · T4 iterate loop |
| 4:15–5:00 | T6 record trace · T7 polish |
| 5:00–5:15 | demo dry-run + buffer |

## Risk register (and the mitigation already designed in)
| Risk | Mitigation |
|---|---|
| deepagents API differs from assumed | Verify early; explicit-orchestration fallback (03) keeps the demo alive. |
| Wifi/API dies at booth | **Mock mode** (`trace.json`) — fully offline replay. |
| Web search flaky/slow/costly | Disk cache + `MAESTRO_OFFLINE` stub. |
| Parallel subagents don't emit clean events | Sequential delegation acceptable for MVP; UI still animates. |
| Time overrun | T1+T4 are independent; cut interview-prep last if needed (keep 4 skills → still "multiple"). |

## Golden rules for builder agents
1. **The event schema (02) is law.** Change it there first, then both sides.
2. **Verify the `deepagents` API from official docs** before building on assumed signatures.
3. **Ship the happy path first**, then add polish. A working 4-skill demo beats a broken 5-skill one.
4. **Mock mode is not optional** — it's the demo's insurance.
5. Keep `ats_score` pure and importable (UI + eval both use it).
6. Never commit secrets; `.env` is gitignored.
