# Architectural Decision Record: Project & Lane Selection

* **Date**: 2026-06-27

## 1. Context & Problem Statement
For The Open Accelerator "Skilled Agents" hackathon (6-hour build window), we needed a project that fit **Lane 3 (Most Innovative Use of Multiple Agents & Skills)**, used LangChain Deep Agents + multi-agent orchestration, and met three explicit constraints: it must **save real time**, be **feasible to implement in 6 hours**, and be **something actual people would use**. Earlier "cool but not useful" concepts (debate arena, knowledge-graph visualizer, newsroom, AI dungeon master) were rejected for lacking genuine utility.

## 2. Options Considered

### Option 1: JobForge — AI job-application kit
* **Description**: Paste a resume + job posting(s) → tailored resume, cover letter, company research, interview prep, and a before/after ATS match score, produced by an orchestrator delegating to specialist subagents.
* **Pros**: Saves 1–3 hrs per application; inputs are pasted text (no OAuth/DB/crawling — avoids hackathon time-sinks); job-seekers in the room are instant users; clean quantitative eval (ATS score before/after) feeds the ADLC loop; natural multi-skill decomposition.
* **Cons**: Resume-tailoring is a crowded space; multi-agent structure is partly manufactured (a single prompt can tailor one resume); innovation score risk for Lane 3.

### Option 2: Contract / ToS Risk Reviewer
* **Description**: Paste a contract → parallel subagents (liability, privacy, termination, payment) flag risky clauses with citations.
* **Pros**: Clear parallel-skill structure; strong B2B utility; precision/recall eval on labeled contracts.
* **Cons**: Narrower user base at the event; less visually exciting; harder ground-truth labeling in 6 hrs.

### Option 3: Dependency / Supply-chain Auditor
* **Description**: Point at a repo → subagents scan for CVEs, license conflicts, abandoned packages → remediation list.
* **Pros**: Genuine engineering value; parallel skills; seeded-vulnerability eval.
* **Cons**: Heavier integration (package ecosystems); narrower demo appeal.

### Option 4: Incident Root-Cause Copilot
* **Description**: Paste logs → parallel subagents pursue different hypotheses → judge ranks causes → draft postmortem.
* **Pros**: Strongest "isolated subagent context" justification; resonates with engineers.
* **Cons**: Needs realistic incident data; harder for a general audience to grasp instantly.

## 3. Chosen Decision & Rationale
**JobForge** was chosen. It best satisfies all three hard constraints simultaneously — high time-savings, low implementation risk (text in/out), and a large, present user base. It also yields a free quantitative eval (ATS match before/after) that directly supplies the ADLC observe→iterate evidence the rubric requires. **Lane 3** confirmed as the target lane.

## 4. Rejected Alternatives
- **Contract Reviewer / Dependency Auditor / Incident Copilot**: all viable and arguably more "innovative," but each trades away either breadth of users (B2B/engineering niches) or implementation safety (data/integration overhead) relative to JobForge.
- **Earlier "cool" concepts** (debate arena, knowledge-graph, newsroom, dungeon master): rejected outright for insufficient real-world utility.
- A noted residual risk: JobForge's innovation ceiling for Lane 3 — mitigated by the architecture/product decisions logged separately (extract-once pipeline, closed scoring loop, batch mode).
