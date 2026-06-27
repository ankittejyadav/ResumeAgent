# Architectural Decision Record: Mock Mode Implementation

* **Date**: 2026-06-27

## 1. Context & Problem Statement
The project spec requires a mock mode that "must look identical to live" and work with the network disabled — the booth's insurance against wifi/API failure. The question was how to implement the paced replay of `trace.json` events in a way that works in all deployment scenarios (local dev, Vercel-hosted frontend, offline booth).

## 2. Options Considered

### Option 1: Server-side SSE replay (`GET /mock`)
* **Description**: FastAPI reads `trace.json`, sleeps `delay_ms/1000` between events, and streams them as SSE. Frontend uses `EventSource('/mock')`.
* **Pros**: Same code path as live mode. `delay_ms` pacing is controlled server-side. Simple frontend.
* **Cons**: Requires the uvicorn server to be running. Doesn't work on Vercel (no persistent server). Original `trace.json` had delays totalling ~53 real seconds — users didn't wait and thought deliverables weren't generated.

### Option 2: Client-side replay with imported JSON (build-time bundle)
* **Description**: Import `trace.json` as an ES module at build time. Replay with `setTimeout` chains in the browser.
* **Pros**: Fully offline, no server needed, zero network calls.
* **Cons**: Trace JSON gets bundled into the JS bundle (increases size). Trace can't be updated without a rebuild.

### Option 3: Client-side replay with runtime fetch (chosen)
* **Description**: `trace.json` lives in `web/public/` (served as a static asset). On mock mode, the frontend `fetch('/trace.json')` at runtime, then replays events with cumulative `setTimeout` chains. `connectMockLocal()` in `eventStore.js`.
* **Pros**: Fully offline once the page is loaded (trace is a static asset served from CDN). Trace can be swapped without a code rebuild (just update the file). Works on Vercel, locally, and with network off after initial page load.
* **Cons**: One extra HTTP request on mock start (to `/trace.json`). Fails if `trace.json` is missing from `public/`.

## 3. Chosen Decision & Rationale
**Option 3 — client-side replay with `fetch('/trace.json')`.**

The `/mock` SSE endpoint (Option 1) was kept in `server.py` for local development convenience, but the primary mock path for deployed and demo use is client-side. This makes mock mode work identically whether the frontend is on Vercel, running via `npm run dev`, or served from a USB drive.

The `delay_ms` values in `trace.json` were also reduced from realistic production timings (~53 seconds total) to a compressed demo pace (~15 seconds total) — fast enough to show the whole flow in a demo without losing the audience.

`_clearMockTimers()` was added so navigating "← New Run" during a replay correctly cancels all pending timeouts.

## 4. Rejected Alternatives
- **Option 1 (server-side SSE)** kept as a secondary path for local dev but not the primary mock mechanism, because it requires uvicorn and has a 53-second real-time pacing problem with the original trace.
- **Option 2 (build-time import)** rejected because it couples the trace to the build; updating the demo trace for a better run would require a full redeploy.
