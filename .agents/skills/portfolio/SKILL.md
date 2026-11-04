---
name: portfolio-documentation
description: >-
  Guides the creation of highly technical, clear, and comprehensive portfolio.md
  files for project repositories, featuring automated tech stack auditing,
  decision log cross-referencing, route directory scanning, architectural
  trade-off tables, and core code snippet extraction.
---

# Portfolio Documentation Authoring Rules

This skill defines the rules and templates for generating a standard, technical `portfolio.md` file at the root of a project repository. This file serves as the source of truth for the developer's automated resume and portfolio website.

---

## 1. Codebase Scan & Audit (Pre-Writing Phase)

Before writing or editing the `portfolio.md` file, you must perform a comprehensive, multi-source scan of the repository. Do not rely on manual memory. Every scan step feeds into **every section** of the output document — tagline, tech stack, achievements, architecture, trade-offs, challenges, and metrics.

### Step 1: Scan Dependency Files
* **JavaScript/TypeScript:** Parse `package.json` dependencies and devDependencies to identify frameworks (e.g. SvelteKit, React), data libraries (e.g. Supabase client, Prisma, Mongoose), drivers (e.g. postgres), migration tools (e.g. drizzle-kit), and build tools (e.g. Vite).
* **Python:** Parse `requirements.txt`, `Pipfile`, or `pyproject.toml` (e.g. Flask, Django, Pandas).
* **Java:** Parse `pom.xml` or `build.gradle` (e.g. Spring Boot, JPA, Hibernate).
* **Other Languages:** Audit Go modules (`go.mod`), Rust configs (`Cargo.toml`), etc.

### Step 2: Scan Infrastructure & Tooling
* Look for configuration files that indicate infrastructure:
  * Presence of `Dockerfile` or `docker-compose.yml` → **Docker** / **Docker Compose**
  * Presence of `.github/workflows/` → **GitHub Actions**
  * Presence of `vercel.json` or `.vercel/` → **Vercel**
  * Presence of `supabase/` folder → **Supabase CLI** / **Supabase**
  * Presence of `netlify.toml` → **Netlify**

### Step 3: Scan Code Files & Imports
* Identify languages by file extensions (`.svelte`, `.ts`, `.js`, `.py`, `.java`, `.go`, `.rs`, `.sql`).
* Search codebase imports to identify integrations and external APIs (e.g. Gmail API, Google Calendar API, Open-Meteo API).

### Step 4: Scan Decision Logs (ADRs)
* Parse all Architectural Decision Record (ADR) files located under `docs/decisions/` (format: `YYYY-MM-DD-*.md`).
* Extract key design context, considered options, trade-offs, chosen rationales, mentioned integrations, removed technologies, and distinct user-facing features.
* **Use ADR findings to inform every section of the portfolio document.** Do not limit ADR incorporation to a subset of sections. Specifically:
  * **Tagline:** Extract all distinct user-facing features, modules, and integrations described across ADRs and ensure every one is represented.
  * **Tech Stack:** Add integrations and APIs discovered in ADRs. If an ADR indicates a technology was removed or purged, **exclude** it from the Tech Stack and do not reference it as a current feature anywhere in the document.
  * **Key Achievements:** Convert major ADR decisions into resume-ready bullet points.
  * **Architectural Trade-offs:** Extract chosen-vs-rejected option comparisons directly from ADR tables.
  * **Technical Challenges:** Convert complex ADR problem/solution narratives into deep-dive entries.
  * **System Metrics:** Extract any performance, latency, or stability data mentioned in ADRs.
* Do not rely solely on dependency scanning (Steps 1-3) for feature or integration discovery — domain features, API integrations, and architectural patterns are often only visible in ADRs and route structures.

### Step 5: Scan Route Directories
* List all top-level directories under the application's routes directory (e.g. `src/routes/`) to discover the full user-facing feature surface area.
* Each route directory typically maps to a distinct product feature or page (e.g. `/workout`, `/life`, `/mail`, `/leaderboard`).
* Cross-reference discovered routes against the tagline and Key Achievements to ensure no shipped feature is omitted from the portfolio document.
* If a route exists in code but has no corresponding ADR, note it and include it in the tagline and achievements based on the route's loader, page component, and server files.

### Step 6: Cross-Reference & Validate
* After completing Steps 1-5, cross-reference all findings to verify:
  * Every technology in the Tech Stack is confirmed by at least one source (dependency file, config file, ADR, or import scan). Remove any that are not.
  * Every user-facing feature discovered via route scanning or ADRs appears in the tagline.
  * No purged or removed technology (identified in ADRs) remains in any section.
  * Every ADR with a substantive architectural decision is represented in at least one of: Key Achievements, Architectural Trade-offs, or Technical Challenges.

---

## 2. Document Template Structure

Generate the `portfolio.md` file matching the following structure. Do not include frontmatter blocks (YAML/JSON). The file should be written in clean, standard markdown.

```markdown
# [Project Name]

[A 2-3 sentence high-level tagline explaining what the system is, who it is for, and its primary value proposition. This tagline must comprehensively list all major user-facing features and integrations discovered during the scan phase.]

## Tech Stack
* **Languages:** [Comma-separated list, e.g. Python, TypeScript, SQL]
* **Frameworks & Libraries:** [Comma-separated list, e.g. SvelteKit, Flask, Spring Boot]
* **Tools & Databases:** [Comma-separated list of databases, drivers, tools, APIs, deployment platforms, and infra, e.g. PostgreSQL, Docker, Google Calendar API, Vercel]

## Key Achievements (Resume Bullets)
* [Action Verb] [Feature/System] [Technical Detail/Implementation] resulting in [Quantifiable Impact or Result].
* [Action Verb] [Complexity/Integration] [Implementation details] to solve [Problem/Challenge].
* [Action Verb] [Infrastructure/Architecture] [Optimizations] to achieve [Performance/Security improvement].

## Core Architecture & Data Flow
[A concise explanation of how components interact and how data flows through the system.]

**Required Mermaid diagram:** Always include a Mermaid `graph TD` diagram. The diagram must NOT be a generic framework request lifecycle (e.g. "server load → SSR → hydrate → client → router → loop"). It must show the specific architecture of this project by including:
* **External APIs:** Every third-party API integration discovered in the scan phase as named nodes (e.g. Gmail API, Google Calendar API, weather APIs, AI APIs).
* **Server layer:** Auth provider, server loaders, form actions / API routes, ORM / database client, and any distinct processing pipelines (e.g. GDPR export, AI triage).
* **Database:** The specific database technology as a named node.
* **Client layer:** Key client-side components and unique UI patterns (e.g. command bar, chat interface, PWA share target).
* **Edges:** Labeled connections showing data flow direction (e.g. OAuth tokens, query results, API calls).
Use `subgraph` blocks to visually group related nodes (e.g. External APIs, Server, Database, Client).

### Architectural Trade-offs
[Present a table showing why specific technologies or patterns were selected over standard alternatives. **Every ADR in `docs/decisions/` that contains a chosen-vs-rejected options comparison must be represented as a row in this table.** After drafting the table, cross-reference it against the full ADR list and add any missing decisions. Closely related ADRs may be combined into a single row only if they address the same architectural concern.]
| Decision | Selected Option | Considered Alternatives | Engineering Rationale |
|---|---|---|---|
| [Category, e.g. State] | [Selected, e.g. Svelte Runes] | [e.g. Redux / RxJS] | [Concrete rationale, e.g. Compile-time reactivity eliminates virtual-dom overhead; keeps bundle size minimal] |

## Technical Challenges & Deep Dives

[Include an entry for every ADR that describes a **non-obvious failure mode**, a **multi-step or creative technical solution**, or a **workaround for a blocked/restricted external dependency**. Not every ADR qualifies — straightforward technology picks that are fully covered by the trade-offs table do not need a deep dive. After drafting, cross-reference against the full ADR list to ensure no complex problem/solution narrative was omitted.]

### 1. [Challenge Name, e.g. Multi-Model Fallback Cascades]
* **Problem:** [Describe why this was difficult and the potential failure modes (e.g. API rate limits, model availability)]
* **Solution:** [Explain the technical solution, including data structures, retry strategies, and design patterns used]
* **Key Takeaway:** [Describe what you learned and the stability/performance result]


## System Performance & Key Metrics
[**Every metric listed must be verifiable** from the codebase, test suite output, build logs, or CI pipeline. Do NOT fabricate or estimate numbers for latency, bundle size, or FCP unless you have run a benchmark or build command that produces the exact figure. Prefer concrete, provable metrics such as:]
* **Test Coverage:** [Number of passing tests and which modules they cover, from `npm test` or equivalent output]
* **Compiler Safety:** [Linter/type-checker results, e.g. svelte-check with zero errors and warnings]
* **Build Integrity:** [Whether the production build completes without errors]
* **Application Scale:** [Route count, ADR count, number of external API integrations, number of database tables — countable from the codebase]
* **Uptime/Stability:** [Specific bugs that were fixed and verified, referencing ADRs. Do not claim "zero errors everywhere" without evidence.]
```

---

## 3. Tone, Formatting & Resume Standards

* **Resume Style:** The bullet points under `## Key Achievements` must begin with strong, professional active verbs (e.g. *Engineered*, *Optimized*, *Architected*, *Implemented*, *Formulated*, *Redesigned*).
* **Technical Depth:** Be extremely precise. Use specific engineering terms (e.g. *PostGIS EWKB coordinate decoding*, *cascade fallback retry states*, *Row-Level Security allowlisting*) rather than generic phrases.
* **No Fluff:** Remove all filler text, welcoming phrases, or subjective statements.

## 4. Execution & File Generation
* Always execute the `write_to_file` tool to create or overwrite the `portfolio.md` file at the root of the repository workspace. Set `Overwrite` to true.
* In the chat response, output a clear summary of the file generation and list the generated content inside a code block for the user's review.
