# Web app and dashboard patterns

Defaults for product software in the browser (SaaS, admin, internal tools, dashboards) as opposed
to marketing websites. The goals are **speed of repeated use, scannability at high density and
keyboard fluency.** Numbers build on the [craft standards](craft-standards.md).

## 1. Application shell

| Region | Default | Notes |
|---|---|---|
| Sidebar navigation | 240–280 px expanded, 56–72 px collapsed | Group by job, max ~7 items per group; current item has background + weight, not colour only |
| Top bar | 48–56 px | Workspace switcher, global search/command, notifications, account |
| Page header | Title (24–28 px) + one-line description + primary action on the right | Breadcrumbs only when hierarchy is ≥ 3 levels |
| Content width | Fluid for tables and boards; 720–960 px for forms and settings | Don't stretch forms to 1600 px |
| Right panel / inspector | 320–400 px | Detail without losing list context |

Collapse the sidebar to a drawer below ~1024 px. Never require horizontal page scroll; tables scroll
inside their own container with sticky first column.

## 2. Density modes

| Mode | Row height | Body size | Use |
|---|---|---|---|
| Comfortable | 48–56 px | 14–15 px | Default, mixed audiences |
| Compact | 36–40 px | 13–14 px | Power users, data-heavy tables |
| Spacious | 64+ px | 15–16 px | Touch-first, low frequency |

Offer a density toggle for heavy tables; keep the same type ramp and only change padding.

## 3. Tables

- Left-align text, right-align numbers, align decimals, tabular figures.
- Header: sortable columns show sort state; sticky header on scroll.
- Row actions: visible on hover/focus for pointer, always visible (overflow ⋯) for touch.
- Bulk actions appear in a contextual bar when rows are selected, with the selection count.
- Empty, loading (skeleton rows), error and "no results for filters" states each designed.
- Pagination for stable datasets with positions that matter; infinite scroll only for feeds.
- Never truncate the identifying column; truncate descriptions with a tooltip/full text on open.

## 4. Filters, search and command

- Filter bar above the table; active filters as removable chips; "Clear all".
- Persist filters in the URL so views are shareable and back works.
- Global **command palette** (⌘K / Ctrl K) for navigation and actions in apps with > ~15 actions.
- Saved views for repeated queries.

## 5. Forms and settings

- Single column, 480–640 px wide fields area; label above field; helper text below.
- Group into sections with headings; long settings use a left sub-navigation.
- Save model: explicit Save for multi-field forms (sticky footer shows unsaved changes); instant save
  for independent toggles with a quiet confirmation.
- Destructive settings in a separate "Danger zone" with typed confirmation for irreversible actions.

## 6. Dashboards

- Start from **decisions**: each widget answers a question someone acts on. Remove vanity widgets.
- Hierarchy: 3–5 KPI tiles on top (value, delta with direction + colour + sign, period, sparkline),
  then trends, then breakdowns, then detail tables.
- KPI number 28–36 px, tabular; label 13–14 px; delta never colour-only (▲/▼ + sign).
- Charts: one message per chart, direct labels over legends where possible, max ~6 categorical
  colours, consistent colour for the same series across charts, y-axis starts at zero for bars.
- Time range selector applies globally and is always visible; show data freshness.
- See `data-visualization-and-dashboard-ux` for chart selection.

## 7. Keyboard and power use

- Every action reachable by keyboard; visible focus everywhere.
- Shortcuts for top actions, discoverable via `?` and in tooltips ("Create  C").
- `Esc` closes overlays; `Enter` submits single-field dialogs; arrow keys move in lists/grids.

## 8. Feedback

- Toasts bottom-left or bottom-centre, 4–6 s, pause on hover, Undo for destructive/bulk actions.
- Long operations: progress in place plus background job indicator; never block the whole app.
- Optimistic updates for low-risk edits; reconcile errors inline.

## 9. Multi-tenant and roles

- Show the current workspace/organisation clearly; switching is explicit.
- Permission-limited UI: hide what the role can never do, disable with explanation what it could do
  with an upgrade or approval.

## 10. Quality check for a web app screen

1. Can a returning user complete the top task in ≤ 3 interactions?
2. Does the screen work at 1280 × 720 without scrolling to the primary action?
3. Is every state (empty, loading, error, no permission) designed?
4. Are numbers aligned and formatted for the locale?
5. Does keyboard-only use work end to end?
