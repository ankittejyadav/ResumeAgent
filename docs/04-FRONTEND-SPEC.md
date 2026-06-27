# 04 — Frontend Spec (Svelte + Vite)

Goal: a **polished, projector-friendly dashboard** that makes the multi-agent orchestration visible and exciting. Dark theme, glassmorphism, smooth transitions. No heavy chart libs — Svelte transitions + SVG/CSS do it.

## Setup
```
cd web
npm create vite@latest . -- --template svelte
npm i
# optional: marked + dompurify for markdown rendering
npm i marked dompurify
```
Dev: `npm run dev` (port 5173). Build: `npm run build` → `web/dist` (can be served by FastAPI).

## Layout (single screen, no scrolling on a 1080p projector)
```
┌───────────────────────────────────────────────────────────────┐
│  HEADER: "JobForge"  · mode badge [LIVE|MOCK] · token/cost HUD  │
├───────────────┬───────────────────────────────┬───────────────┤
│ SkillShelf    │      AgentGraph (center)      │  ScoreDial     │
│ (5 skill      │  orchestrator node + 5        │  before→after  │
│  cards, light │  subagent nodes; edges pulse  │  % climbing,   │
│  up when      │  on delegation; status rings) │  keyword chips │
│  loaded/active│                               │  red→green     │
├───────────────┴───────────────────────────────┴───────────────┤
│ TodoPanel (plan checking itself off)  │  Deliverables (tabs:   │
│                                        │  Resume/Cover/Company/ │
│ ActivityLog (streaming lines)          │  Interview, copy btn)  │
└───────────────────────────────────────────────────────────────┘
```
Before a run: a clean **input screen** — two textareas (Resume, Job posting), sample-data button, big **"Forge ✦"** button, and a **mode toggle** (Live / Mock).

## Components
- **`App.svelte`** — input screen ↔ dashboard; owns run lifecycle: `POST /run` → `connect(run_id)` (live) or `connectMock()` (mock).
- **`lib/eventStore.js`** — SSE client + the `state` store (see 02). One `apply(evt)` reducer. Mock mode: fetch `/mock` via EventSource too (server paces it), OR import `trace.json` and dispatch on `delay_ms`.
- **`ScoreDial.svelte`** — animated radial gauge. Tweened value (`svelte/motion` `tweened`). Shows before (ghost) and after (solid) + delta badge "+41". Keyword chips below.
- **`TodoPanel.svelte`** — list with status icons (○ pending, ◐ in_progress spinner, ● done). `flip`/`fade` transitions on update.
- **`AgentGraph.svelte`** — SVG: central orchestrator node, 5 subagent nodes in an arc. Edge to a subagent **pulses/animates** while `activeAgents` contains it. Node ring color by status. Pure SVG + CSS keyframes; no graph lib needed.
- **`SkillShelf.svelte`** — 5 cards (name, model badge Haiku/Sonnet, description tooltip). Dim until `skill_loaded`, glow while active.
- **`Deliverables.svelte`** — tabbed; renders `content_markdown` via `marked`+`dompurify`; per-tab **Copy** button.
- **`ActivityLog.svelte`** — auto-scrolling feed of `log` + key lifecycle lines, color by level.

## Visual design tokens
- Background: deep navy→charcoal radial gradient. Panels: `rgba(255,255,255,0.04)` + `backdrop-filter: blur(12px)` + 1px subtle border.
- Accent: electric cyan `#22d3ee` (active), lime `#a3e635` (done/matched), rose `#fb7185` (missing/error), amber for in_progress.
- Font: Inter / system stack. Generous spacing. Rounded-2xl cards. Soft shadows.
- Motion: 200–400ms ease transitions; the score dial is the hero animation — make it satisfying.

## Mock mode (demo safety) — MANDATORY
- Toggle on the input screen. In mock mode, ignore the API and replay `trace.json` (bundled in `web/src/` or fetched from `/mock`).
- Must look identical to live. This is the fallback if wifi/API dies on stage. **Test it offline.**

## Markdown safety
Always run `content_markdown` through `dompurify` before `{@html}`.

## Acceptance (frontend)
- Input screen → "Forge" starts a run and the dashboard animates from real SSE events.
- Score dial visibly climbs before→after; missing keywords turn matched.
- All 4 deliverables render and are copyable.
- Mock mode replays a full run with the network disabled.
