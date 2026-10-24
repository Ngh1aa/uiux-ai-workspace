---
name: data-tables-and-enterprise-ux
description: Design dense data interfaces with sorting, filtering, selection, batch actions, pagination, responsive behavior and accessibility. Use for dashboards, admin, CRM, directories and enterprise tools.
---

# Data Tables & Enterprise UX

## Goal and scope

Let expert users find, compare and act on many records quickly and safely. A good enterprise table is a work surface: the columns map to decisions, the selection model is unambiguous, bulk actions cannot surprise anyone, and state (sort, filter, page, selection) survives the moves users actually make. The output is a table spec that engineering can build without inventing behavior.

**When not to use**

- Charts, KPI tiles and trend monitoring: use [data-visualization-and-dashboard-ux](../data-visualization-and-dashboard-ux/SKILL.md).
- Global search across content types, autocomplete and result pages: use [site-search-and-findability](../site-search-and-findability/SKILL.md). Table-scoped filtering stays here.
- Editing one record in a long form or wizard: use [complex-forms-and-wizards](../interaction-patterns-and-form-ux/references/complex-forms-and-wizards.md).
- Long-running bulk jobs after the user clicks the action (queues, partial failure, retries): use [complex-workflow-and-progress-ux](../interaction-patterns-and-form-ux/references/complex-workflow-and-progress-ux/README.md).
- Token and component API for the table component itself: use [design-system-and-components](../design-system-and-components/SKILL.md).

## Decisions

**1. Columns follow decisions, not the schema**
- For each column write the decision it supports. No decision, no default column; move it to a details view or the column picker.
- First column is the record identifier users recognize (name, not internal ID), and it is the row's link target.
- Order: identifier, status, the two or three comparison fields, then secondary data, then row actions at the end.
- Numbers right aligned with tabular figures and consistent decimals; text left aligned; units in the header, not in every cell.
- Truncate long text with full value available on hover and focus, never truncate identifiers to ambiguity.

**2. Density modes**
- Offer density as a user preference when the audience mixes scanning experts and occasional users. Typical modes: compact, default, comfortable (IBM Carbon and Atlassian both ship size variants; verify current row heights in the chosen system).
- Default density for mixed audiences; compact for expert, high-volume work; comfortable when rows contain wrapped text, avatars or touch targets.
- Density never shrinks interactive targets below the platform minimum; on touch, keep rows tall enough for the target size required by your accessibility baseline.
- Zebra striping helps on wide tables with many columns; on narrow tables, row dividers are enough.

**3. Sticky and frozen regions**
- Sticky header whenever the table scrolls vertically inside the page or exceeds one viewport.
- Freeze the identifier column (and selection checkbox) when the table scrolls horizontally.
- Sticky bulk-action bar appears when one or more rows are selected and replaces or sits above the header toolbar.
- Do not nest scroll containers more than one level; double scrollbars break keyboard and trackpad use.

**4. Sort, filter and persistence**
- Single-column sort by default, with visible direction indicator on the active column only and `aria-sort` on that header. Multi-sort only for analyst tools, with sort order displayed.
- Default sort is stated and meaningful (for example "Last updated, newest first"), never database order.
- Filters show as removable chips with a single "Clear all". Results count updates with filters.
- Persist sort, filters, column choice and density per user, and reflect sort, filter and page in the URL so views are shareable and the back button works.

**5. Selection and bulk actions**
- Checkbox column for multi-select; header checkbox selects the current page and is tri-state (none, some, all on page).
- After selecting the full page, offer "Select all N matching results" explicitly; the count is always visible ("24 selected").
- Selection persists across pagination only if the UI shows that it does; otherwise clear it on page change and say so.
- Bulk action bar lists only actions valid for the whole selection; if some rows are ineligible, state how many will be skipped before running.
- Destructive bulk actions: confirmation names the count and object type ("Delete 24 invoices"), and undo is preferred over a modal when the action is reversible.
- Row actions: one primary inline action at most, the rest in an overflow menu with an accessible name that includes the row ("Actions for Invoice 1042").

**6. Pagination vs infinite scroll vs virtualization**
- **Pagination**: default for enterprise tables. Choose when users need a stable position, refer to rows by location, select across sets, or return via back button. Show page size control and total when it is cheap to compute.
- **Load more / infinite scroll**: for feed-like browsing where position does not matter and there is no footer content. Avoid for tables with bulk selection.
- **Virtualization**: for very large client-side datasets that must feel continuous (logs, spreadsheets). It is an implementation technique, so it still needs a correct row count for assistive tech (`aria-rowcount`, `aria-rowindex`), and in-page find (Ctrl+F) will not see unrendered rows, so provide table search.
- Server-side sort and filter whenever the dataset is not fully loaded; never sort only the visible page.

**7. Responsive fallback**
- First try: fewer default columns plus horizontal scroll with frozen identifier.
- On small screens, switch to a list or card layout only if the task is lookup, not comparison. Keep the same sort, filter and primary actions.
- Never hide the column that the primary decision depends on.

**8. Semantics and ARIA**
- Static data: native `<table>` with `<caption>` (or accessible name), `<th scope>` headers. This is the default.
- Sortable columns: a button inside the `<th>`, `aria-sort` on the active header only (WAI-ARIA APG sortable table example).
- Interactive cell navigation (spreadsheet-like editing, arrow keys between cells): `role="grid"` per the APG grid pattern, with one tab stop and arrow-key movement. Do not use `grid` for a read-only table.
- Announce result-count changes after filtering via a polite live region.

## Workflow

1. Start from user decisions and actions, not database columns; list top tasks and the column each needs (Decision 1).
2. Prioritize columns and choose density intentionally (Decision 2), including sticky and frozen regions (Decision 3).
3. Define sort, filter, search and persistence behavior, including URL state and defaults (Decision 4).
4. Design row selection, batch actions and destructive safeguards (Decision 5).
5. Choose pagination, infinite or virtualization based on task and data volume (Decision 6).
6. Design responsive fallback without destroying comparison (Decision 7).
7. Specify accessible names, headers, sort state and keyboard interaction (Decision 8).
8. Define table states: loading (skeleton rows), empty first-use, no results for filter (with clear filters action), error with retry, permission-limited.

Read [table patterns reference](references/table-patterns.md) when you need row height guidance, bulk-action edge cases, keyboard maps for grid vs table, or a filled spec example.
Before handoff run [table gate](checklists/table-gate.md).

**Anti-patterns**

- Columns mirroring the API response, including internal IDs and created_by UUIDs as default columns.
- Header checkbox that silently selects all 10,000 records, or only the page without saying so.
- Bulk delete that runs on rows hidden by a filter the user forgot was active.
- Sorting only the loaded page of a server-paginated dataset.
- Infinite scroll on an admin table, so the footer and the selected row are unreachable and the back button loses position.
- Sort icons on every column at all times, so the active sort cannot be told apart.
- `role="grid"` on a static table, which removes normal reading navigation for screen reader users.
- Row click that opens a record and also toggles selection.
- Filters reset on navigation back from a detail page.
- Horizontal scroll with no frozen identifier, so users lose which row they are reading.

**Output**

A table spec containing:
1. Purpose, primary user and top three tasks.
2. Column table:

| Column | Decision supported | Data type and format | Align | Default visible | Sortable (default dir) | Filterable (control) | Width rule | Mobile behavior |
|---|---|---|---|---|---|---|---|---|

3. Interaction spec: default sort, filter model, selection model, bulk actions with eligibility and confirmation copy, row actions.
4. Volume strategy: pagination, load more or virtualization, with rationale and page size.
5. State spec: loading, empty, no results, error, permission.
6. Accessibility spec: semantics (table or grid), caption, aria-sort, keyboard map, live region messages.

## Quality gate

- PASS only if headers and table purpose are programmatically clear (caption or accessible name, `th` with scope).
- PASS only if sort state is visible on the active column and announced via `aria-sort`.
- PASS only if selection and action relationship is unambiguous: selected count is visible and bulk actions state their scope.
- PASS only if mobile alternative preserves core tasks and the primary decision column.
- PASS only if every default column maps to a written decision.
- PASS only if sort, filter and page state survive back navigation.
- PASS only if destructive bulk actions name the count and object, and offer undo or confirmation proportional to reversibility.
- FAIL if sort or filter operates on the visible page only while data is server paginated.

**Baseline / sources**

- IBM Carbon data-table usage and accessibility guidance.
- Atlassian Design System dynamic table; Material Design data tables; verify current row heights and variants.
- WAI-ARIA Authoring Practices: table, sortable table example, grid pattern.
- Nielsen Norman Group articles on data tables and bulk actions (general guidance, no figures assumed).
