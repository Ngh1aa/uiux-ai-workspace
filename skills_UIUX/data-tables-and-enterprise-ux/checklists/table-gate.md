# Table Gate

Mark each item PASS or FAIL with evidence.

- [ ] Table has a caption or accessible name; headers are `th` with correct scope.
- [ ] Active sort column shows direction and carries `aria-sort`; no other header carries it.
- [ ] Default sort is meaningful and stated.
- [ ] Every default column maps to a written decision.
- [ ] Sort and filter run server-side when data is paginated or partially loaded.
- [ ] Sort, filter, page and density survive back navigation; view state is in the URL.
- [ ] Selected count is always visible; header checkbox scope (page vs all matching) is explicit.
- [ ] Changing filters clears or explicitly preserves selection, with notice.
- [ ] Bulk actions state eligible and skipped counts before running.
- [ ] Destructive actions name count and object; undo or confirmation matches reversibility.
- [ ] Row action menus have accessible names including the row identifier.
- [ ] `role="grid"` is used only when cell-level keyboard navigation is the task.
- [ ] Virtualized tables expose `aria-rowcount` and `aria-rowindex`, and offer in-table search.
- [ ] Mobile layout keeps the primary decision column and primary actions.
- [ ] Loading, empty, no-results, error and permission states are designed.
