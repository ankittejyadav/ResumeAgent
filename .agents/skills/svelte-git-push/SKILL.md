---
name: svelte-check-pre-push
description: Protocol for running svelte-check validation and pushing code safely to GitHub on Windows machines.
---

# Svelte-Check & Git Push Protocol

This skill details how to perform pre-push code verification using `svelte-check` on Windows (bypassing execution policy restrictions) and commit/push changes safely to GitHub.

## Pre-Verification Checks

### 1. Unused CSS Selectors
Ensure no unused CSS selectors remain in Svelte components:
- **Action:** Remove the unused classes from the `<style>` block if they are dead code.
- **Alternative:** If the styles target dynamically rendered or child-component elements, wrap the selector in `:global(...)` (e.g., `:global(.active-class)`).

### 2. Accessibility (a11y) Warnings on Modal Backdrops
Ensure modals are accessible and do not trigger a11y linter warnings:
- **Action:**
  1. Set `role="presentation"` on the outer overlay (backdrop).
  2. Set `role="dialog"`, `aria-modal="true"`, and `tabindex="-1"` on the inner modal content container.
  3. Use Svelte ignore comments above the elements containing `onclick` handlers on presentation elements:
     ```svelte
     <!-- svelte-ignore a11y_click_events_have_key_events -->
     <!-- svelte-ignore a11y_no_static_element_interactions -->
     <div class="modal-overlay" onclick={handleClose} role="presentation">
     ```

## Verification & Deployment Workflow

### 1. Run Pre-Push Checks
Before staging any changes, run the Svelte diagnostic compiler checks directly using Node to check for type, syntax, or import errors:
```powershell
node node_modules/svelte-check/bin/svelte-check --fail-on-warnings
```

If any compilation errors or unused CSS selectors are found, fix them before proceeding.

### 2. Compile Production Build
Verify that the code compiles into a production bundle successfully:
```powershell
node node_modules/vite/bin/vite.js build
```

### 3. Commit and Push to GitHub
Once both the check and the production build pass, commit the files and push to GitHub:
```powershell
git add .
git commit -m "your commit message"
git push
```
