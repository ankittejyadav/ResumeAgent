---
name: design
description: Guidelines for eliminating external icon dependencies, standardizing consistent card component composition, uniform interactive hover highlights, and minimalist page structures.
---

# Design & Icon Simplification Guidelines

To prevent compilation breaks (such as missing exports in third-party icon libraries like `lucide-svelte`), this skill establishes a protocol for replacing package-dependent icons and complex inline SVGs with simple, pure CSS and HTML alternatives.

## Protocol for Icon Replacement

When refactoring pages to remove external icon dependencies:

### 1. Brand Logo Replacement (CSS/Text Placeholders)
Instead of importing brand-specific SVGs (which can change or break between library versions), replace brand logos with stylized CSS containers displaying the first letter of the vendor or a clean text tag.

**Before (Package Import / Custom SVG):**
```html
<script>
  import GithubIcon from "lucide-svelte/dist/icons/github";
</script>

<div class="logo">
  <GithubIcon size={24} />
</div>
```

**After (Simplified CSS Initials):**
```html
<div class="logo-fallback" style="background: var(--brand-color);">
  <span>G</span>
</div>
```

### 2. Standardize on Centralized Material Symbols
If a functional UI icon is strictly necessary (e.g. settings cog, checkmark, close cross), use the project's centralized [Icon.svelte](file:///absolute/path/to/project/src/lib/ui/Icon.svelte) component.
* Avoid importing individual icons from `lucide-svelte` or any external package.

* Use: `<Icon name="settings" size={18} />`

### 3. Page Header Minimalism & Safe Area Spacing
* Page headers must remain clean and minimalist.
* Do not display page titles, names, or taglines/subheadings at the top of pages.
* Do not include back arrows or back-navigation buttons at the top of pages. Navigation should be handled by the main application shell layouts (e.g., sidebars or global menus).
* Ensure adequate top spacing/padding is provided at the very top of pages (e.g., utilizing CSS environment variables like `safe-area-inset-top` or equivalent fallback paddings) to prevent hardware features like phone notches or status bars from overlapping application content.

### 4. Mobile Shell & Persistent Navigation Header
* To prevent mobile navigation elements (such as floating hamburger menus or drawer triggers) from overlapping page content:
  * Do not use fixed-floating buttons that overlay arbitrary page sections.
  * Establish a persistent, sticky mobile header bar at the top of the application viewport on mobile devices.
  * Render all mobile navigation/drawer triggers inside this header bar.
  * Ensure the header accommodates hardware notches using safe area environment variables (`safe-area-inset-top`).
  * Render all page-specific body content below this header bar within the layout flow.

### 5. Card Component & Interactive Grid Consistency
* Always wrap list entries, dashboard grids, and module cards inside the project's centralized Card components rather than designing ad-hoc containers or flat HTML lists.
* Use global stylesheet modifiers or component-level global selectors (e.g., Svelte `:global()`) to propagate custom card configurations cleanly without breaking compilation scope rules.
* Standardize interactive grid action or "Add" card hover backgrounds using the project theme's central primary accent variables rather than inline or ad-hoc background values.
* Avoid nesting translucent or glassmorphic elements inside parent wrappers that have background fills, as this alters the backdrop opacity and perceived background color of the cards.
* When rendering multiple collections of selectable items on a dashboard (e.g. categories or options), avoid nesting them in custom list styles or grouped container panels. Render them as a flat, uniform grid of card components matching the style and layout density of other pages in the module to maintain a cohesive visual system.
* Sibling card components inside the same module must maintain matching visual action headers. If one card class features top action triggers (such as absolute-positioned edit/pencil and delete buttons), sibling card classes must render matching edit/delete action alignments to ensure a uniform interactive footprint across all grids.





### 6. Verification Steps
After removing icon imports, always run:
1. Sveltekit Sync:
   `node node_modules/@sveltejs/kit/svelte-kit sync`
2. Vite Build Check:
   `node node_modules/vite/bin/vite.js build`
