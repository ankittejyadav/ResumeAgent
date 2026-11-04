---
name: skill-creator
description: Guidelines and rules for creating or modifying custom agent skills in the workspace.
---

# Skill Creation & Modification Guidelines

This skill defines the requirements, layout, and structure parameters for adding or modifying workspace skills.

## Rules & Requirements

1. **Storage Location:**
   - Always place the skill directory under `skills/<skill_name>/` (relative to the customization root directory, e.g. [skills](file:///absolute/path/to/project/.agents/skills/)).
   - Folders should be named using kebab-case.


2. **File Structure & Layout:**
   - **SKILL.md:** Every skill must contain a `SKILL.md` file at the root of its folder.
   - **Support Directories (Optional):**
     - `scripts/`: Executable scripts and helper utilities.
     - `examples/`: Reference implementations and examples.
     - `resources/`: Configuration templates and static files.
     - `references/`: Extended documentations and notes.

3. **SKILL.md Frontmatter:**
   - Every `SKILL.md` file must begin with valid YAML frontmatter containing `name` and `description` parameters:
     ```yaml
     ---
     name: unique-skill-name
     description: Concise statement of what this skill does and when the agent should trigger it.
     ---
     ```
   - Only the frontmatter is matched by the agent processor to automatically discover and load skills.

4. **Instruction Constraints:**
   - Keep the main instruction body inside `SKILL.md` under 500 lines.
   - Offload raw documentation, specifications, or excessive text lists into files inside the `references/` subdirectory, and point the agent to load them.

5. **Absolute Path References:**
   - Always write file links inside the instructions using their absolute `file://` system paths, including their parent folders, to avoid duplicate basename confusion (e.g. referencing `[code-preferences/SKILL.md](file:///absolute/path/to/project/.agents/skills/code-preferences/SKILL.md)`).


6. **Genericity and Reusability:**
   - Guidelines and rules in skills must be kept generic and high-level so they can be reused across different files, projects, and users.
   - Avoid hardcoding specific route paths, namespaces, page names, or user parameters inside rules unless specifically formatted as an illustrative example.

7. **Read Target Skills in Full First:**
   - Before modifying any custom skill in the workspace (including this one), you must always execute a full-file read of the target `SKILL.md` file (by calling `view_file` without line range constraints) to verify that you are conforming to its existing patterns and frontmatter parameters.


