# 00 — Project Brief & Context

This doc captures **everything** decided during planning so a fresh agent can build without the original chat.

---

## 1. The hackathon

**The Open Accelerator — "Skilled Agents" / "Wicked Smart Agents"**, Boston (Fort Point), **Saturday June 27, 2026, 9:30 AM–6:00 PM**. ~100 builders, teams ≤5. **Build window: 10:45 AM–4:00 PM (~6 hours).**

Theme: build shippable agent **skills** and prototypes anchored to the **`agentskills.io` open standard**, with discipline around **model selection** and the **Agent Development Life Cycle (ADLC)**.

Sponsors: **Anthropic** ($50 Claude API credits/attendee), Red Hat, IBM/IBM Ventures, Commonwealth of MA (Mass AI Hub).

### Lanes
- **Lane 1** — Build an agent + skill from scratch.
- **Lane 2** — Best improved agent/skill (fork "BriefingClaw"; baseline by 10:30, only deltas scored).
- **Lane 3 — Most Innovative Use of Multiple Agents and Skills.** ← **WE ARE IN LANE 3.** Compose multiple agents + skills into novel systems via multi-agent orchestration, delegation, or skill composition.

### Judging — 80 points
| Criterion | Pts | What it means for us |
|---|---|---|
| **Shippability & Spec Conformance** | 25 | It runs. Skills pass `skills-ref validate`. Public repo, README, OSI license. |
| **ADLC Discipline** | 20 | Evidence across phases; completed worksheet with **≥1 evaluate/observe loop**. |
| **Lane-Specific Merit** | 20 | Lane 3 = orchestration novelty. |
| **Skill Quality** | 15 | Grounded expertise, coherent units, good defaults, documented gotchas, output templates. |

**Strategic read:** ~45 of 80 pts are engineering hygiene + a quantitative loop. The win is a *focused* system done with rigor, not an ambitious system that half-works. Our before/after ATS score IS the ADLC quantitative loop — most teams fumble this; we get it for free.

### Hard rules
- Document **model-selection rationale** (cost/latency/quality) — mandatory worksheet field.
- All skills must validate via `skills-ref validate`.
- ADLC worksheet completion mandatory.
- Public repo + OSI-compliant license (we use **MIT**).

---

## 2. The product — "JobForge"

**One-liner:** Paste a resume + a job posting → in ~60s get a tailored resume, custom cover letter, company research, and interview prep (likely questions + STAR-format draft answers), plus a **before/after ATS match score**.

**Why this project** (the three criteria the user demanded):
1. **Saves a lot of time** — people spend 1–3 hours tailoring *each* application and apply to dozens. Collapses to ~1 minute.
2. **Feasible in 6 hours** — inputs are *pasted text*. No Gmail OAuth, no auth'd crawling, no database (the classic hackathon time-sinks are avoided). Web search is bounded + cached.
3. **Real users in the room** — a large share of hackathon attendees job-hunt; instant live testers.

**Why it's genuinely multi-agent (not one prompt):**
- Parallel specialist subagents, each backed by a `SKILL.md`.
- An **independent ATS/keyword-match scorer** that must be *separate* from the resume-tailor — a checker shouldn't grade its own work. This is the concrete justification for Deep Agents' **isolated subagent contexts**.

---

## 3. The five skills (one SKILL.md each → one subagent)
| Skill | Model | Role |
|---|---|---|
| `resume-tailor` | Sonnet 4.6 | Rewrite resume bullets to match the job's keywords/requirements. |
| `cover-letter` | Sonnet 4.6 | Draft a tailored cover letter. |
| `company-research` | Haiku 4.5 + web | Summarize the company (mission, recent news, values) from live search. |
| `interview-prep` | Sonnet 4.6 | Likely interview questions + STAR-format draft answers grounded in the resume. |
| `ats-scorer` | Haiku 4.5 | Compute keyword/requirement match % vs. the job posting. Runs on the ORIGINAL (before) and the TAILORED (after) resume. **Independent checker.** |

Orchestrator runs on **Sonnet 4.6**.

---

## 4. Locked decisions (confirmed with the user — do NOT reopen)
| Decision | Choice |
|---|---|
| Lane | **Lane 3** (multi-agent / skill composition) |
| Project | **JobForge** AI application kit |
| Agent framework | **LangChain Deep Agents** (`deepagents`, Python) |
| Backend | **Python + FastAPI**, **SSE** transport |
| Frontend | **Svelte + Vite** (fallback: pure-Python **NiceGUI** only if no JS capacity) |
| Web search | **Live** web search + **cache** for determinism/demo safety |
| Skill count | **All 5** from the start |
| Models | Haiku 4.5 (extract/score) · Sonnet 4.6 (write/orchestrate) |
| License | **MIT** |
| Demo safety | **Mock mode** replays a recorded `trace.json` through the same UI |

### Model IDs (verify before use)
- Sonnet: `claude-sonnet-4-6`
- Haiku: `claude-haiku-4-5-20251001`
- (Opus, if ever needed: `claude-opus-4-8`)

---

## 5. Key external facts (verified during planning, re-verify if blocked)

**LangChain Deep Agents (`deepagents`)** — batteries-included agent harness on LangGraph:
- Planning tool `write_todos` (structured task list in agent state) — drives our live todo panel.
- **Subagents** with **isolated context**: the main agent only receives a subagent's final result, not its intermediate tool calls. This is core to our design.
- Context offloading/compression + prompt caching built in.
- Create with `model`, `tools`, `system_prompt`, and `subagents`.
- Runs on LangGraph → stream events via `astream_events` (this is how we feed the UI).
- Docs: https://docs.langchain.com/oss/python/deepagents/overview · Repo: https://github.com/langchain-ai/deepagents

**`agentskills.io` / Agent Skills standard:**
- A skill = a folder with a `SKILL.md` (YAML frontmatter + Markdown body).
- Required frontmatter: `name` (≤64 chars, lowercase/numbers/hyphens), `description` (≤1024 chars, non-empty, "what it does + when to use").
- Optional: `license`, `compatibility` (≤500 chars), `metadata` (arbitrary key-values). Optional dirs: `scripts/`, `references/`, `assets/`.
- Validate: `skills-ref validate path/to/skill` (install the `skills-ref` reference lib; exec lands on PATH in the venv).
- Spec: https://agentskills.io/specification · Repo: https://github.com/agentskills/agentskills

> ⚠️ **Important nuance:** `SKILL.md` is natively a Claude Code / OpenCode construct, NOT a native deepagents concept. **Our novelty is the bridge:** a `skill_loader` reads each `SKILL.md` and constructs a deepagents subagent from it (body → system prompt, frontmatter description → subagent description used for delegation routing). See `01-ARCHITECTURE.md`.

---

## 6. Demo narrative (what the judges see)
1. Paste a real resume + a real job posting. Hit **Forge**.
2. Orchestrator plans → **todo list** appears and checks itself off.
3. **ats-scorer** runs first → baseline **match score** shows (e.g. 48%).
4. Four specialist subagents light up and work **in parallel**; missing keywords shown in red.
5. ats-scorer re-runs on the tailored resume → score **climbs to ~89%**, keywords turn green.
6. Four polished deliverables assemble on screen; user can copy each.
7. Mention: live web search for company research, model-selection rationale, and the eval table.
