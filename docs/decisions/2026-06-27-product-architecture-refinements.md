# Architectural Decision Record: Product & Token-Efficiency Refinements

* **Date**: 2026-06-27

## 1. Context & Problem Statement
A critique of the initial JobForge design surfaced three product risks that would make it lose to the "just do it myself" alternative: (1) for a *single* application, multi-agent orchestration is **slower and more token-expensive** than one well-crafted prompt; (2) a spectator "watch the agents" UI is **bad UX** for a user who just wants the output; (3) feeding full resume + full job posting to every subagent **wastes tokens** (same context paid for ~5×). We needed the architecture to genuinely beat the manual baseline, not just look impressive.

## 2. Options Considered

### Option 1: Ship the original design as-is
* **Description**: Orchestrator + 5 subagents each receiving raw resume + posting; orchestration dashboard as the primary UI.
* **Pros**: Simplest; matches the first spec.
* **Cons**: Higher cost + latency than a single prompt for one job; spectator UX; multi-agent framing is decorative, not load-bearing.

### Option 2: Refined pipeline (extract-once + closed loop + parallel DAG + batch + output-first UI)
* **Description**: A cheap extraction pass produces a structured requirement list (from the posting) and fact list (from the resume); subagents work from those compact artifacts. The independent scorer drives a tailor→score→re-tailor loop. Subagents run as a true dependency DAG for latency. Adds a batch mode (one resume × many postings). UI streams editable deliverables first; agent visualization is secondary.
* **Pros**: Cuts input tokens; measurably better output than one-shot (closed loop); genuinely beats manual at scale (batch); good real-user UX.
* **Cons**: More implementation work on already-built code; requires a migration/diff rather than a clean build.

### Option 3: Abandon multi-agent, use a single strong prompt
* **Description**: One prompt does everything for one job.
* **Pros**: Cheapest/fastest for a single application.
* **Cons**: Forfeits Lane 3 (multi-agent) entirely; no objective scoring loop; no batch leverage.

## 3. Chosen Decision & Rationale
**Option 2.** The refinements are what make the multi-agent architecture *earn its cost* rather than be decoration:
- **Extract once**: Haiku turns posting→requirements and resume→facts; pass these compact artifacts (not raw text) to each subagent — large input-token reduction and a shared, consistent brief.
- **Closed loop**: the independent `ats-scorer` feeds missing keywords back to `resume-tailor` so output is measurably better than one-shot.
- **True parallel DAG**: `extract ∥ company-research ∥ score-before` → `resume-tailor` + `interview-prep` (parallel) → `cover-letter` → `score-after`; wall-clock = longest chain, the only way multi-agent competes with a single streaming prompt on speed.
- **Batch mode**: one resume × several postings → ranked match table + a kit per job; this is where automation decisively beats the manual baseline.
- **Output-first UX**: stream editable deliverables as they complete (first useful content <10s); the agent-graph visualization is the garnish, not the main event.

## 4. Rejected Alternatives
- **Option 1 (ship as-is)**: rejected — it would lose to a single prompt on cost/latency for the common single-job case, and its UX makes users wait as spectators.
- **Option 3 (single prompt)**: rejected — forfeits the Lane 3 multi-agent thesis, the objective scoring loop, and batch leverage; only wins the narrow single-job latency case the batch+DAG design already addresses.
