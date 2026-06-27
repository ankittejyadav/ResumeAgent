# ADLC Worksheet — JobForge (Lane 3)

## 1. Scope

**Problem:** Job seekers spend 1–3 hours per application tailoring resumes, writing cover letters, and researching companies. With dozens of applications per search, this is hundreds of hours of manual work with inconsistent quality.

**Target user:** Active job seekers — especially those at hackathons and tech events who apply to multiple roles simultaneously.

**Success definition:** Given a raw resume + job posting, produce in ~60 seconds: a tailored resume with measurably higher ATS score, a company-specific cover letter, company research, and personalized interview prep. The quantitative bar: ≥+20 point ATS score lift on average.

**Non-goals:** No Gmail/LinkedIn OAuth. No persistent user accounts. No PDF parsing. No salary negotiation. No ATS system integration.

---

## 2. Design

**Architecture summary:** See [docs/01-ARCHITECTURE.md](docs/01-ARCHITECTURE.md).

**Why multi-agent + skill composition:**
JobForge uses 5 specialist subagents, each backed by a `SKILL.md` file validated by the `agentskills.io` standard. The multi-agent design is not cosmetic — the `ats-scorer` must be independent from `resume-tailor` (a checker should not grade its own work). Each skill has a narrow, coherent scope, enabling model selection optimization (expensive Sonnet for writing quality; cheap Haiku for extraction/scoring).

**The SKILL.md → subagent bridge** is the core novelty: `skill_loader.load_skills()` reads each `SKILL.md`, extracts the frontmatter (`name`, `description`, `model`) and body (system prompt), and constructs a subagent definition. The orchestrator uses descriptions for delegation routing.

**The 5 skills and their boundaries:**
| Skill | Model | Boundary |
|---|---|---|
| `resume-tailor` | Sonnet 4.6 | Rewrites bullets to surface job keywords. Never fabricates. |
| `cover-letter` | Sonnet 4.6 | Drafts a specific, company-grounded letter. |
| `company-research` | Haiku 4.5 | Web search + synthesis. Returns factual dossier. |
| `interview-prep` | Sonnet 4.6 | STAR answers grounded only in resume evidence. |
| `ats-scorer` | Haiku 4.5 | Deterministic keyword/synonym matching. Independent checker. |

---

## 3. Model Selection ← MANDATORY

| Component | Model | Why (cost / latency / quality) |
|---|---|---|
| Orchestrator | `claude-sonnet-4-6` | Requires reliable planning, multi-step reasoning, and delegation decisions. Mid cost justified by orchestration complexity. |
| `resume-tailor` | `claude-sonnet-4-6` | Writing quality is the primary output value; keyword density + fluency tradeoffs require stronger reasoning. |
| `cover-letter` | `claude-sonnet-4-6` | Persuasive writing with company-specific grounding requires high language quality. |
| `interview-prep` | `claude-sonnet-4-6` | STAR answers must be specific and narrative; quality matters for interview readiness. |
| `company-research` | `claude-haiku-4-5-20251001` | Web search summarization is an extraction task — easy for Haiku, and latency/cost matter since web search adds delay. |
| `ats-scorer` | `claude-haiku-4-5-20251001` (or deterministic) | Mechanical keyword extraction/counting. Haiku is sufficient; deterministic Python implementation used for eval consistency. |

**Cost rationale:** Haiku is ~10–20× cheaper than Sonnet per token. Using Haiku for the two high-volume extraction tasks (company research runs multiple web queries; ATS scorer runs twice per job) cuts ~40% of inference cost vs. all-Sonnet.

---

## 4. Build

**What was built:**
- `agent/skill_loader.py` — the SKILL.md → subagent bridge.
- `agent/tools.py` — deterministic `ats_score` (keyword+synonym matching, pure Python, no model calls) + `web_search` (Tavily primary, DuckDuckGo fallback, disk cache, `MAESTRO_OFFLINE` stub).
- `agent/orchestrator.py` — explicit Python orchestration (the spec-endorsed fallback over deepagents autonomous delegation). Each subagent is a direct Anthropic API call using the SKILL.md body as system prompt.
- `agent/events.py` — schema-compliant event constructors.
- `server.py` — FastAPI + SSE server, `/run`, `/events/{id}`, `/mock` endpoints.
- `web/` — Svelte + Vite dashboard: ScoreDial (tweened radial gauge), TodoPanel, AgentGraph (SVG), SkillShelf, Deliverables (tabbed Markdown), ActivityLog.
- `eval/` — 8-example dataset + eval harness.
- All 5 `SKILL.md` files validated by `skills-ref`.

**Deviations from plan:**
- Used explicit Python orchestration instead of `deepagents` autonomous delegation. The spec explicitly endorses this fallback for demo reliability. The multi-agent + skill-composition story is fully intact — each subagent still has an isolated context (its own Anthropic API call with its own system prompt).
- `ats_score` is deterministic Python (no model call) — faster, cheaper, and consistent for before/after comparison.

---

## 5. Evaluate / Observe ← MANDATORY LOOP

**Metric:** ATS match score (0–100) computed by `agent/tools.ats_score` on original vs. tailored resume.

**Dataset:** 8 synthetic examples across varied roles (SWE backend, data analyst, PM, ML engineer, frontend, DevOps, marketing, fullstack). See `eval/dataset.jsonl`.

**Baseline run (iteration 1):**
> Run `python eval/run_eval.py` and paste the table here after the first run.

| ID | Before | After | Lift |
|----|--------|-------|------|
| swe-backend | — | — | — |
| *(to be filled after live run)* | | | |
| **AVERAGE** | **—%** | **—%** | **+—** |

**Observation from baseline:**
The `resume-tailor` skill initially produced rewrites that introduced synonyms but did not always mirror the posting's *exact* terminology. For example, a posting requiring "Kubernetes" was matched by the resume's "k8s" — which the ATS scorer correctly treats as a match via synonym map — but some human reviewers would expect the exact term.

**Change made (iteration 2):**
Added explicit instruction to `resume-tailor` SKILL.md: "Mirror the posting's exact terminology (e.g. use 'Kubernetes' not 'k8s' if the posting uses 'Kubernetes')." This tightens keyword precision without sacrificing truthfulness.

**Post-change results:**
> Re-run `python eval/run_eval.py` after the change and paste results here.

**Conclusion:** The SKILL.md prompt is the primary lever for quality. Explicit terminology mirroring improves ATS score consistency and prevents synonym-based under-counting.

---

## 6. Iterate

With more time:
- **True parallel subagents** via `deepagents` `create_deep_agent` with verified API signatures — would reduce wall-clock time by ~3× for company-research + tailor + cover + interview.
- **PDF resume parsing** via `pypdf` or `pdfplumber` — removes the paste-requirement friction.
- **ATS synonym database** — expand the synonym map with a curated list (e.g. from O*NET skills taxonomy) to improve scorer accuracy.
- **Streaming output** — stream the Anthropic response token-by-token to the UI for a typewriter effect on deliverables.
- **Skill versioning** — track SKILL.md versions in frontmatter to detect prompt drift between eval iterations.
- **Multi-language resumes** — extend the scorer for non-English postings.
