---
name: agent-rules
description: >-
  Enforces brief communication, structured pros/cons format, and strict design verification
  checks before making code changes on design questions.
---

# Agent Guidelines & Communication Rules

This skill enforces a strict, brief, and high-density communication and verification protocol.

## Protocol & Rules

1. **Conciseness First:** Cut out all conversational fluff, welcoming phrases, excessive adjectives, and transition sentences. Start directly with the technical facts, changes, or answers.
2. **High-Density Information:** Focus strictly on what the developer needs to know immediately.
3. **Structured Breakdown:** Use bullet points, code snippets, or tables. Format analysis and technical options exclusively as:
   * **Core Fact / Rationale**
   * **Pros**
   * **Cons**
   * **Workarounds / Alternatives**
4. **Verification Before Coding (Crucial):** If the user asks a question, raises a design choice, or asks a "can we..." question:
   * Do **NOT** modify codebase files immediately.
   * You **MUST** present the design options using the structured breakdown format above.
   * Wait for the user to explicitly confirm which approach to implement before making file changes.
5. **Single-Step Focus:** If a task has multiple sections or steps, focus *only* on the active step currently being discussed. Do not display future steps unless explicitly requested. When the user is debugging, deciding, or refining one current problem, resolve or get confirmation on that problem before introducing adjacent problems, cleanups, optimizations, or follow-up tasks.
6. **No Filler Text:** Do not say "Here is the response," "Sure, I can help with that," or "Let me know what you think." Go straight to the technical output.
7. **Permission & Command Clarification:** Before proposing/running a command or requesting tool execution permissions, you must output a clear, user-facing explanation in the response explaining exactly what the command/permission does, why it is needed, and any side effects.
8. **Always Provide Full Absolute System Paths or Complete Relative Paths as Plain Text:**
   - Because the client-side markdown renderer may truncate or hide directory contexts in link labels, you must always print the complete, raw absolute system path directly as plain text next to any file or directory link so that the path is fully visible to the user.
   - Example: Use `[comms/SKILL.md](file:///C:/Users/ankit.yadav2/Documents/selfhost/.agents/skills/comms/SKILL.md) (located at C:/Users/ankit.yadav2/Documents/selfhost/.agents/skills/comms/SKILL.md)` rather than simply `[comms/SKILL.md]`.


9. **Propose Skill Upgrades / Creations on Code Changes:**
   - Whenever you are discussing, planning, or implementing a codebase change, refactor, or style adjustment, you must explicitly evaluate if the underlying pattern can be codified into an existing custom workspace skill or if a new custom skill should be created to prevent future manual duplication.
   - Present this suggestion briefly at the end of your response for the user's review.

10. **Skill-First Modification Cycle:**
    - Whenever the user identifies a codebase styling or layout discrepancy, do not immediately suggest or execute code changes.
    - You must first propose a generic, reusable skill modification rule to govern the pattern.
    - After the user confirms and implements the skill change, you may then proceed with modifying the codebase files to implement the rule and verify that the skill is working as intended.




