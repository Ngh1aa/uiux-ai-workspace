# Table Patterns Reference

Read this when choosing row heights and density, handling bulk-action edge cases, writing keyboard maps, or when you need a filled table spec to copy.

## Density and row height
- Design systems ship named size variants rather than one row height. IBM Carbon offers several row sizes from extra small to extra large; Atlassian and Material offer compact and default variants. Verify current values in the system you build on rather than copying numbers from memory.
- Rule of thumb: pick the smallest density at which the row still contains one line of primary text, a readable secondary line if needed, and interactive targets that meet your accessibility baseline (WCAG 2.2 target size minimum, or platform guidance on touch).
- Wrapping text, avatars, tags or inline editing push the row to the next size up. Do not mix heights within one table except for expanded rows.
- Persist density per user; default is the middle variant.

## Column width rules
- Identifier: flexible, minimum width so typical names do not truncate.
- Status: fixed, wide enough for the longest status label plus icon.
- Numbers and dates: fixed to the widest formatted value; right aligned.
- Free text (description, notes): takes remaining space, truncated with full text on hover and focus and in the detail view.
- Allow column resize only for analyst audiences; persist it.

## Selection model edge cases

| Situation | Behavior |
|---|---|
| Header checkbox clicked, more pages exist | Select current page, show banner "25 on this page selected. Select all 1,240 matching results?" |
| "Select all matching" active, user changes filter | Clear selection and announce it; never carry an "all" selection into a new result set |
| Selection exists, user paginates | Either keep selection with a persistent count ("31 selected across pages") or clear it with notice; decide once and document |
| Some selected rows ineligible for an action | Keep action enabled, confirmation states "18 will be archived, 6 skipped (already archived)" |
| Action partly fails on the server | Result summary with counts and a filter to show failed rows; see complex-workflow-and-progress-ux for job handling |
| Row deleted by another user | Row shows removed state on next refresh; selection count updates |

## Bulk action bar
- Appears on first selection, shows count, lists actions, has "Clear selection".
- Primary and frequent actions visible; rest in overflow.
- Destructive action uses the destructive style and confirmation copy with count and noun.
- Prefer undo (toast with Undo for a reasonable window) for reversible actions such as archive; use a confirmation dialog for irreversible actions such as permanent delete.

## Pagination details
- Show range and total ("1 to 50 of 1,240") when the total is cheap; otherwise "Next" without a total and say "1,000+".
- Page size options limited to a few sensible values; remember the choice.
- Keep pagination controls in the same place on every page; put them below the table and optionally above for long pages.
- Cursor-based APIs can still back a paginated UI with next and previous, without jump-to-page.

## Keyboard maps

### Static or sortable table (native table)
- Tab moves through interactive elements: sort buttons in headers, row links, checkboxes, row action buttons.
- Enter or Space on a sort button toggles sort; `aria-sort` updates on that `th` and is removed from the previously sorted header.
- Screen reader table navigation works natively; do not intercept arrow keys.

### Grid (interactive cells, per WAI-ARIA APG grid pattern)
- One tab stop into the grid (roving tabindex); Tab leaves the grid.
- Arrow keys move cell focus; Home and End move within the row; Ctrl+Home and Ctrl+End move to first and last cell.
- Enter or F2 enters edit mode in an editable cell; Escape cancels edit and returns focus to the cell.
- Use only when cell-level navigation is the task (spreadsheets, editable matrices).

### Virtualized rows
- Set `aria-rowcount` on the table or grid to the full count and `aria-rowindex` on rendered rows.
- Keep focus stable when rows recycle; do not move focus to a different record on scroll.

## Live region messages
- After filter: "Showing 42 results" (polite).
- After bulk action: "24 invoices archived. Undo available." (polite).
- After error: message in the visible error region; use assertive only for blocking failures.

## Worked example: Invoices table

### Before
- 14 default columns straight from the API including `id`, `customer_uuid`, `created_by`, `updated_at`.
- Infinite scroll; header checkbox selected all loaded rows silently; "Delete" in the toolbar always enabled.
- Sort icons on every header; sorting happened client-side on loaded rows only.

### After
- Default columns: Invoice (link), Customer, Status, Amount (USD, right aligned), Due date, Days overdue, Actions. Others in column picker.
- Default sort: Days overdue, descending, because the primary task is chasing overdue invoices.
- Pagination 50 per page with total; sort and filters in the URL; server-side sort.
- Selection: page-level header checkbox plus "Select all matching" banner; count in sticky bulk bar.
- Bulk actions: Send reminder, Export, Archive (undo toast), Delete (confirmation: "Delete 24 invoices permanently? This cannot be undone.").

### Filled column row

| Column | Decision supported | Data type and format | Align | Default visible | Sortable (default dir) | Filterable (control) | Width rule | Mobile behavior |
|---|---|---|---|---|---|---|---|---|
| Days overdue | Which invoices to chase first | Integer, "0" shown as "Not due" | Right | Yes | Yes (desc, default sort) | Range: 1 to 30, 31 to 60, 60+ | Fixed to widest value | Shown as badge on card |

## Sources
- IBM Carbon data table: usage, style and accessibility tabs.
- Atlassian Design System dynamic table; Material Design data tables.
- WAI-ARIA Authoring Practices Guide: table pattern, sortable table example, grid pattern, data grid examples.
- WCAG 2.2 target size; verify current guidance.
