# 05 — Skills Spec (the five SKILL.md files)

Each skill is `skills/<name>/SKILL.md`: YAML frontmatter + Markdown body. The body becomes the subagent's system prompt, so write it as **expert instructions to the agent**, not docs about the agent. Skill-quality points (15) come from: grounded expertise, coherent scope, sensible defaults, **documented gotchas**, and an **output template**. Include those sections in each body.

## Validation (must pass)
```
pip install skills-ref          # or per agentskills repo instructions
skills-ref validate skills/resume-tailor
# ... repeat for all 5; CI-style: for d in skills/*/; do skills-ref validate "$d"; done
```
Frontmatter rules: `name` ≤64 chars, `[a-z0-9-]` only, must match folder name. `description` non-empty ≤1024 chars, state **what it does + when to use it** (the orchestrator routes on this).

## Common body template (use for all five)
```markdown
---
name: <kebab-name>
description: <what it does and when to use it — used for delegation routing>
license: MIT
metadata:
  model: <claude-haiku-4-5-20251001 | claude-sonnet-4-6>
  lane: "3"
---

# <Title>

## Role
One paragraph: the expertise this agent embodies.

## Inputs
What it receives (resume text, job posting, prior agent outputs).

## Method
Numbered steps the agent should follow. Be specific and opinionated (this is the "grounded expertise").

## Defaults
Sensible default choices (tone, length, format) when input is ambiguous.

## Gotchas
- Known failure modes and how to avoid them. (Required for skill-quality points.)

## Output template
The exact structure/Markdown the agent must produce.
```

---

## 1. `resume-tailor` (Sonnet)
- **description:** "Rewrites and reorders resume bullet points to match a specific job posting's keywords and requirements, without inventing experience. Use when tailoring a resume to a target role."
- **Method highlights:** extract the job's hard requirements + ATS keywords; map each to existing resume evidence; rewrite bullets to surface matched keywords using strong action verbs + quantified impact; reorder for relevance; NEVER fabricate.
- **Gotchas:** don't keyword-stuff; preserve truthfulness; keep to 1 page worth; mirror the posting's terminology (e.g. "RAG" vs "retrieval").
- **Output template:** the full tailored resume in Markdown (sections: Summary, Experience bullets, Skills) + a short "Changes made" note.

## 2. `cover-letter` (Sonnet)
- **description:** "Drafts a tailored, specific cover letter for a given resume + job posting + company context. Use after company research is available."
- **Method:** hook referencing the company/role; 2 body paras tying resume evidence to the role's needs; close with enthusiasm + call to action. Use company-research output if present.
- **Defaults:** ~250–350 words, confident-not-arrogant tone, no clichés ("team player", "fast learner").
- **Gotchas:** avoid generic letters; reference something specific about the company; match company voice.
- **Output template:** salutation → body → sign-off, Markdown.

## 3. `company-research` (Haiku + web_search)
- **description:** "Researches a company using live web search and summarizes mission, products, recent news, and culture signals to inform applications. Use to ground cover letters and interview prep."
- **Method:** derive company name from job posting; run 2–3 focused `web_search` queries (about page, recent news, values); synthesize; cite sources inline.
- **Gotchas:** dedupe stale/marketing fluff; flag when info is thin; never fabricate facts — say "not found".
- **Output template:** sections — One-liner, What they do, Recent news (dated), Culture/values, Sources.

## 4. `interview-prep` (Sonnet)
- **description:** "Generates likely interview questions for a role and drafts STAR-format answers grounded in the candidate's resume. Use to prepare a candidate for a specific job."
- **Method:** infer question themes from the job's responsibilities; produce 6–8 likely questions (mix behavioral + role-specific); for each, a STAR (Situation, Task, Action, Result) answer drawn ONLY from resume evidence.
- **Gotchas:** answers must be grounded in the resume, not invented; keep each STAR tight; include 2 questions for the candidate to ask back.
- **Output template:** numbered Q → STAR blocks; final "Questions to ask them" list.

## 5. `ats-scorer` (Haiku) — the independent checker
- **description:** "Scores how well a resume matches a job posting's keywords and requirements, returning a 0–100 match score plus matched and missing keywords. Use to measure tailoring effectiveness before and after."
- **Method:** extract the posting's required skills/keywords/requirements into a checklist; check presence in the resume (case/stem-insensitive); score = matched/total ×100; list matched + missing.
- **Defaults:** weight explicit "required"/"must have" items higher than "nice to have".
- **Gotchas:** synonyms count as matches (e.g. "JS"≈"JavaScript"); don't reward keyword-stuffing without context; be consistent so before/after is comparable.
- **Output template:** JSON-ish block `{value, matched_keywords, missing_keywords}` AND a one-line rationale. (The Python `ats_score` tool in `tools.py` is the authoritative scorer used by the UI + eval; this skill mirrors it for any agent-driven scoring. Keep them consistent.)

> Decision to make at build time: either (a) `ats-scorer` subagent just calls the Python `ats_score` tool, or (b) it scores via the model. **(a) is recommended** — deterministic, importable by eval, demo-safe. Keep the SKILL.md so the spec-conformance/skill-quality story stays intact (it documents the scoring method).
