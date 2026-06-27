# Architectural Decision Record: Vercel Deployment Strategy

* **Date**: 2026-06-27

## 1. Context & Problem Statement
JobForge needs a public URL for the hackathon demo and judges. The project has two parts: a Python FastAPI backend (SSE, AI calls) and a Svelte/Vite frontend. Vercel is the preferred hosting target because of its GitHub integration and zero-config deploys. The challenge: a live AI run takes ~60 seconds, and Vercel's serverless function timeout is 10 seconds on Hobby plans — making live backend calls impossible on Vercel.

An additional complication: Vercel auto-detected `server.py` + `requirements.txt` in the repo root and deployed FastAPI instead of the Svelte frontend, returning `{"detail":"Not Found"}` to all browser requests.

## 2. Options Considered

### Option 1: Full-stack on Vercel (FastAPI + Svelte)
* **Description**: Deploy FastAPI as Vercel serverless functions alongside the static Svelte build.
* **Pros**: Single URL, no separate backend hosting needed.
* **Cons**: Serverless timeout (10s Hobby / 60s Pro) kills any live run over ~10 seconds. SSE streaming is unreliable in serverless. Would require Vercel Pro at minimum.

### Option 2: Frontend on Vercel, backend elsewhere (Railway/Render/Fly.io)
* **Description**: Deploy the Svelte app to Vercel as a pure static site. Deploy FastAPI to a persistent server (Railway, Render, Fly.io). Wire them together via `VITE_BACKEND_URL` env var.
* **Pros**: No timeout issues. Vercel serves the static UI fast from CDN.
* **Cons**: Two services to manage. Live mode requires the backend URL configured in Vercel env vars.

### Option 3: Frontend on Vercel with client-side mock (chosen)
* **Description**: Deploy only the Svelte frontend to Vercel. Mock mode fetches `trace.json` from `/public/` and replays it entirely client-side using `setTimeout` chains — no server contact at all. Live mode uses `VITE_BACKEND_URL` pointing at a local or separately-hosted backend.
* **Pros**: Demo works fully offline (critical for booth/wifi-failure scenario). Zero backend cost on Vercel. Simple single deployment.
* **Cons**: Live mode requires a separately running backend. `VITE_BACKEND_URL` must be set for production live runs.

## 3. Chosen Decision & Rationale
**Option 3 — frontend-only on Vercel with client-side mock.**

The hackathon demo relies on mock mode as its safety net (per the project spec). Making mock completely self-contained in the browser eliminates all infrastructure risk at the booth: no wifi dependency, no API key dependency, no server process dependency. Judges see the full animated demo regardless of network conditions.

For live mode, the backend runs locally (`uvicorn server:app`) and the frontend connects to `http://localhost:8000` by default — exactly how it's developed anyway.

The Vercel auto-detection conflict was resolved by:
1. Setting **Root Directory** to `web/` in Vercel project settings.
2. Adding `web/vercel.json` with `{"framework": "vite"}` so Vercel skips Python detection.

## 4. Rejected Alternatives
- **Option 1 (full-stack on Vercel)** rejected because the 10-second serverless timeout makes any real AI run impossible on Hobby tier. Even on Pro (60s), a slow API response or web search could exceed the limit.
- **Option 2 (separate backend service)** not needed for the hackathon. Added complexity (two services, two URLs, CORS management) with no benefit given that mock mode is the primary demo path.
