# Architectural Decision Record: Orchestration Approach

* **Date**: 2026-06-27

## 1. Context & Problem Statement
JobForge is built for Lane 3 (multi-agent orchestration). The original plan was to use `deepagents` (`create_deep_agent`) for autonomous agent delegation — the model decides when to call which subagent, driven by their descriptions. The risk: the `deepagents` API surface (exact function signatures, event emission, `astream_events` mapping) had not been verified against current docs at build time, and fiddly event mapping under a 6-hour hackathon time budget could kill the demo.

## 2. Options Considered

### Option 1: deepagents autonomous delegation
* **Description**: Use `create_deep_agent` with `subagents=` kwarg. Let the model plan and delegate autonomously. Map `astream_events` output to the schema-02 event types.
* **Pros**: Truest multi-agent story. Native `write_todos` planning tool. Most innovative use of the framework.
* **Cons**: API shape unverified. `astream_events` → schema mapping is complex and error-prone under time pressure. Any SDK version mismatch silently breaks the demo.

### Option 2: Explicit Python orchestration (chosen)
* **Description**: Each subagent is a direct `anthropic.AsyncAnthropic().messages.create()` call with the SKILL.md body as the system prompt. The Python orchestrator drives the sequence, emits events explicitly, and wraps each call in try/except.
* **Pros**: Zero framework risk. Clean, predictable event emission. Errors are always caught. Easy to debug. The multi-agent story is intact — each subagent has an isolated context (its own API call, its own system prompt, no shared state).
* **Cons**: Does not use `deepagents` for the actual autonomous delegation. Less "innovative framework use" — but the SKILL.md bridge is still the core novelty.

## 3. Chosen Decision & Rationale
**Option 2 — explicit Python orchestration.**

The spec (doc 03) explicitly endorses this fallback: *"If `astream_events` mapping proves fiddly under time pressure, the fallback is to NOT use full autonomy: orchestrate the steps explicitly in Python... The multi-agent + skill-composition story holds either way."*

The SKILL.md → subagent bridge (`skill_loader.py`) is the genuine novelty for Lane 3 judges: reading a validated `agentskills.io` skill file and constructing an isolated agent context from it. Whether that context is invoked by an autonomous framework or explicit Python doesn't change what the judges care about — isolated subagents, skill composition, before/after ATS score.

A top-level `try/except` wrapper was added so orchestrator crashes emit a `log(error)` + `done` event instead of silently hanging the UI.

## 4. Rejected Alternatives
- **Option 1 (deepagents autonomous)** rejected under time pressure. The `deepagents` package is still in `requirements.txt` (demonstrates framework adoption) and `ADLC.md` documents the deviation and rationale. If time allows post-hackathon, migrating to true autonomous delegation is the natural next step.
