# Architectural Decision Record: Tech Stack & Multi-Agent Architecture

* **Date**: 2026-06-27

## 1. Context & Problem Statement
JobForge needed a stack that (a) runs LangChain Deep Agents, (b) streams live orchestration to a UI for a compelling demo, (c) is buildable in 6 hours, and (d) conforms skills to the `agentskills.io` standard (`skills-ref validate`). The central design question was how to compose `SKILL.md` skills — natively a Claude Code / OpenCode construct — into Deep Agents subagents, and what transport/frontend to use.

## 2. Options Considered

### Agent framework
* **LangChain Deep Agents (`deepagents`, Python)** — built-in planning (`write_todos`), subagents with isolated context, context offloading, prompt caching. Chosen: matches the hackathon theme and the user's stated preference.

### Frontend
### Option 1: Svelte + Vite
* **Description**: Lightweight reactive UI with `EventSource` SSE client.
* **Pros**: Best animation/polish per line of code; no virtual-DOM overhead; minimal boilerplate; great for the live orchestration visuals.
* **Cons**: Adds a JS toolchain alongside the Python backend.

### Option 2: React / Next.js
* **Description**: Component framework / full SSR framework.
* **Pros**: Largest ecosystem; "production" feel.
* **Cons**: Heaviest setup for a 6-hour build; more boilerplate than needed.

### Option 3: Pure-Python UI (NiceGUI / Streamlit)
* **Description**: Keep everything in Python.
* **Pros**: One language; fast wiring to FastAPI.
* **Cons**: Fights custom animation (score dial, agent graph, live highlights) — weak on the "cool/good-looking" requirement.

### Backend / transport
* **FastAPI + SSE** vs. WebSocket: SSE chosen — one-way server→UI push is all the live event stream needs; simpler than WebSocket.

### Web search (for `company-research`)
* **Live + disk cache** vs. offline-only: live chosen (per user) for real company lookups, with a cache for determinism, cost control, and demo safety.

## 3. Chosen Decision & Rationale
- **Agents**: LangChain Deep Agents (Python).
- **Skill composition (the novelty)**: a `skill_loader` reads each `skills/<name>/SKILL.md`, mapping the body → subagent system prompt and frontmatter `description` → delegation-routing hint. One SKILL.md = one specialist subagent. This bridges the `agentskills.io` standard to Deep Agents and is the core innovation claim.
- **Backend**: Python + FastAPI, **SSE** event stream; in-memory `run_id → asyncio.Queue` event bus; agent events mapped from LangGraph `astream_events` to a fixed event schema (the backend/frontend contract).
- **Frontend**: **Svelte + Vite**, chosen over React/Next (too heavy) and Python UIs (poor custom animation). NiceGUI retained only as a fallback if no JS capacity.
- **Models**: Haiku 4.5 (extraction/scoring/research) · Sonnet 4.6 (writing/orchestration).
- **Web search**: live (Tavily/DuckDuckGo) + disk cache.
- **Skills**: all 5 from the start; **License**: MIT.
- **Demo safety**: a **mock mode** replays a recorded `trace.json` through the identical UI with no network.

## 4. Rejected Alternatives
- **React / Next.js**: setup cost not justified for a 6-hour, single-screen dashboard.
- **Pure-Python UI (NiceGUI/Streamlit)**: insufficient for the custom animated visuals; kept only as an emergency fallback.
- **WebSocket transport**: unnecessary bidirectionality vs. SSE for a one-way event stream.
- **Offline-only research**: rejected in favor of live search (with caching to recover determinism and demo robustness).
