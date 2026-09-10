# Ngh1aa Repository Hub — Redesign Concept

A static redesign concept for the public repository experience of the **Ngh1aa** GitHub organization.

## Why this exists

GitHub owns the native layout and CSS of `https://github.com/orgs/Ngh1aa/repositories`, so a repository cannot directly reskin that page. This prototype explores the experience the organization *would* present if its repositories were treated as a coherent product/design archive rather than an alphabetical code list.

The concept can later become:

- a standalone GitHub Pages portfolio/index;
- the content/design basis for an organization profile README once an organization-level `.github` repository exists;
- a visual test fixture for UIUX Factory's rendered QA and 56-rule Evidence Contract.

## Design direction

**Editorial technical archive** rather than generic developer dashboard.

The page organizes the organization around four narratives:

1. **AI / design infrastructure** — `uiux-ai-workspace`, `skills_UIUX`, `uiux-factory`.
2. **Product systems** — `StudioOS`, `FlowCRM`, `HireFlow` and other application experiments.
3. **Commerce studies** — `Atelier`, `LuxRoom`, `VioletMarketplace`.
4. **Redesign studies** — `Capital`, VAS/Vietbank/Capital redesign repositories.

Featured project descriptions are grounded in the corresponding repository READMEs where available. Repositories without enough inspected project context use neutral labels in the explorer instead of invented product claims.

## Interaction

- Search repositories by name or discipline.
- Filter by AI/systems, product, commerce, redesign or tooling.
- Keyboard-focusable controls and repository rows.
- 44px minimum filter/button targets on the responsive implementation.
- `prefers-reduced-motion` disables non-essential transition duration.
- Responsive layouts for large desktop, tablet and mobile widths.

## Run locally

From this directory:

```bash
python -m http.server 4173
```

Then open:

```text
http://localhost:4173/
```

No dependencies or build step are required.

## Files

```text
index.html   semantic page structure and featured projects
styles.css   visual system and responsive layout
app.js       public repository data, search and filter behavior
```

## Source boundary

Only public repository names are included in the prototype. Private repository names or metadata are intentionally not published into this static showcase.
