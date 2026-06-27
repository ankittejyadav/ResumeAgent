"""
server.py — FastAPI + SSE server for JobForge.
"""
import asyncio
import json
import pathlib
from uuid import uuid4

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.events import sse
from agent.orchestrator import orchestrate

app = FastAPI(title="JobForge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

runs: dict[str, asyncio.Queue] = {}

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


class RunIn(BaseModel):
    resume: str
    job_posting: str


@app.post("/run")
async def run_endpoint(body: RunIn):
    rid = uuid4().hex
    q: asyncio.Queue = asyncio.Queue()
    runs[rid] = q

    async def emit(evt):
        await q.put(evt)

    asyncio.create_task(orchestrate(body.resume, body.job_posting, emit))
    return {"run_id": rid}


@app.get("/events/{rid}")
async def events_endpoint(rid: str):
    if rid not in runs:
        raise HTTPException(status_code=404, detail="run not found")
    q = runs[rid]

    async def gen():
        while True:
            evt = await q.get()
            yield sse(evt)
            if evt.get("type") == "done":
                break

    return StreamingResponse(gen(), media_type="text/event-stream", headers=SSE_HEADERS)


@app.get("/mock")
async def mock_endpoint():
    trace_path = pathlib.Path("trace.json")
    if not trace_path.exists():
        raise HTTPException(status_code=404, detail="trace.json not found — run a live session first")

    events = json.loads(trace_path.read_text(encoding="utf-8"))

    async def gen():
        for evt in events:
            delay = evt.pop("delay_ms", 0) / 1000
            if delay > 0:
                await asyncio.sleep(delay)
            yield sse(evt)
            if evt.get("type") == "done":
                break

    return StreamingResponse(gen(), media_type="text/event-stream", headers=SSE_HEADERS)


# Serve built Svelte app if available
_dist = pathlib.Path("web/dist")
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="static")
