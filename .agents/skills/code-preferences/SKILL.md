---
name: minimalist-data-development
description: Enforces the elimination of mock data, requires safe empty/fallback states to prevent crashes, permits hardcoding only when strictly necessary, and enforces a minimalist visual/UX style.
---

# Minimalist & Real-Data Development Guidelines

This skill enforces strict rules around mock data removal, safety boundaries, hardcoding restrictions, and minimalist design.

## Rules & Principles

1. **No Mock Data:**
   - Do not use mock data files, objects, or static mock values for application state.
   - All components and pages must load data directly from the server or database.

2. **Safe Fallbacks (No-Crash Policy):**
   - When real data is absent, the application must not crash or display raw error codes.
   - Render clean, functional empty states or "unconfigured" indicators (e.g., "Connect Google Calendar to see your schedule" or "Log your first meal to track macros").
   - Handle database nulls and API request failures gracefully.

3. **No Hardcoding unless Absolutely Necessary:**
   - Values like timezones, API endpoints, location coordinates, usernames, and goals must be dynamic and loaded from database rows or secure environment configurations.
   - Hardcoding is only permitted for configuration defaults (like `DEFAULT_TIMEZONE = 'America/New_York'`) when database-level values are missing.

4. **Minimalist Aesthetics:**
   - Design layouts to be highly functional, clean, and uncluttered.
   - Avoid excessive visual decorations, mesh backgrounds, or complex gradients unless requested.
   - Prioritize high-quality typography, clean borders, structured white space, and clear contrast.
   - Rely strictly on CSS variables defined in the central theme rather than ad-hoc inline styles.

5. **Component Modularity & Single-Responsibility:**
   - Avoid creating large, monolithic layout components (e.g. dashboards) that aggregate multiple distinct functionalities (such as AI recommendations, input fields, and grids).
   - Break down complex layout views into highly cohesive, single-responsibility sub-components under `src/lib/` to ensure reusability, testability, and isolated local state scope.

6. **Consistent Naming Conventions & Domain Alignment:**
   - **Svelte Components:** Always name Svelte component files using PascalCase (e.g., `AiRecommendationCard.svelte`, `RoutinePromptInput.svelte`, `SplitGrid.svelte`).
   - **Backend Helpers & Utilities:** Use kebab-case for database helper files, backend utility scripts, and server actions (e.g., `workout-db.js`, `date-utils.js`).
   - **API Directories:** Name routing and API endpoints folders using kebab-case (e.g., `/gym/api/start-session/`, `/gym/api/end-session/`).
   - **Domain Context Alignment:** Ensure that page-level route folders (e.g., `/gym`) and their corresponding library folders or backend helper files (e.g., `src/lib/workout` or `workout-db.js`) use matching, unified context names to prevent cognitive mismatch, unless a component or utility is explicitly designed for general-purpose reuse across multiple route domains. Verify this alignment manually by executing:
     `node .agents/skills/code-preferences/scripts/audit-names.cjs`

7. **Composition over Configuration (Shared UI Elements):**
   - When multiple domain-specific components (e.g. `SplitGrid` and `ExerciseGrid`) share layout designs, do not merge them into a single monolithic component controlled by multiple conditional config parameters.
   - Instead, keep the components separate and modular, and compose them by nesting the domain content inside generic, style-only wrapper components (such as `Card.svelte` or layout wrappers) using Svelte slots/snippets.

8. **Visual & Layout Consistency in User Flows:**
   - Ensure that components presenting related domain objects (such as splits and exercises) maintain consistent layout containers (e.g., all lists or all card grids) across sequential steps in the same user workflow.
   - Avoid mixing raw list rows and card grids for identical semantic items unless strictly required by mobile-notch constraints or explicit viewport limits.

9. **Direct Database Sourced State (No Independent UI State Divergence):**
   - The primary goal of this application is to serve as a user-facing interface to interact with and persist state in the database.
   - Everything rendered or happening on the UI must derive directly from database rows.
   - The UI state must never diverge from or exist independently of the database state. Any action, selection, or transition performed by the user should be immediately synchronized with or loaded from the database, allowing full control of the application state simply by interacting with the database.

10. **Minimum Viable Complexity & Database Truth:**
   - Build the smallest database-backed solution that makes the core user workflow function correctly.
   - Avoid extra tables, metadata fields, derived fields, aliases, hidden normalization rules, caches, or multi-step abstractions unless they are required for the current basic functionality.
   - Prefer deleting or simplifying logic over adding new layers when the behavior can be represented directly by existing database rows.
   - The UI must show users what is actually true in the database, not a cleaned-up or inferred version that hides confusing stored state.
   - If stored data is incomplete, ambiguous, or unconfigured, show a clear database-backed empty or incomplete state instead of inventing fallback meaning in the app layer.

11. **Mock Datatypes Matching Production:**
    - All mock data used in test fixtures and test environments (e.g., in unit tests) must accurately represent actual production database driver types.
    - Specifically, database timestamp columns (such as `created_at`, `started_at`, `ended_at`) must return Javascript `Date` objects rather than ISO string literals to match the real behavior of `postgres.js` in production, and sentinel values/unset states must match actual production constants.

12. **Omit File Extensions on Alias Imports:**
    - Do not use file extensions (like `.js` or `.ts`) when importing files using SvelteKit path aliases (such as `$lib/mock/data`).
    - Specifically, import like `import { ... } from "$lib/mock/data"` instead of `"$lib/mock/data.js"`.
    - This avoids Vite/SvelteKit alias resolution failures and duplicate module instantiation errors (which can trigger server-side 500 compilation or runtime errors during deployments).
