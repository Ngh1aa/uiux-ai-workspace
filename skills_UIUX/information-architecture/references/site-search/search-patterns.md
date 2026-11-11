# Search Patterns Reference

Read this when specifying combobox keyboard behavior, facet logic, zero-result layouts, building the query test set, or when you need a worked example.

## Combobox keyboard map (WAI-ARIA APG combobox with listbox popup)
- Typing: updates the input and opens the popup when there are suggestions.
- Down Arrow: opens the popup if closed; moves highlight to the next option. Focus stays in the input; the highlighted option is referenced by `aria-activedescendant`.
- Up Arrow: moves highlight to the previous option.
- Enter: if an option is highlighted, selects it (query suggestion runs that search; instant result navigates). If none is highlighted, runs a full search on the typed text.
- Escape: closes the popup and keeps the typed text; a second Escape may clear the field if the product chooses, documented.
- Tab: leaves the field; does not select a suggestion silently.
- Required attributes: input has `role="combobox"`, `aria-expanded`, `aria-controls` pointing to the listbox, `aria-autocomplete` (list or both), an accessible label. Options have `role="option"` and `aria-selected` on the highlighted one. Group headings use `role="group"` with a label.
- Announce the number of suggestions via a polite live region after typing pauses, not on every keystroke.

## Suggestion groups and limits
- Recent searches (on empty focus), query suggestions, instant results (top items by type). Each group labeled.
- Keep each group short so the popup fits the viewport above the mobile keyboard.
- Debounce requests; show nothing rather than stale suggestions for a previous query.
- Never show suggestions that lead to zero results.

## Facet logic

| Situation | Rule |
|---|---|
| Multiple values in one facet | OR (Color: Red or Blue) |
| Values across facets | AND (Color: Red and Size: M) |
| Hierarchical facet (category tree) | Selecting a parent includes children; show breadcrumb of selection |
| Numeric range | Slider plus input fields; presets for common ranges |
| Value count after other filters | Count reflects current other selections (disjunctive counts within the same facet) |
| Zero-count values | Hide or disable consistently; never let them produce an empty page |

Facet order: by usage from analytics or research, not alphabetical. Collapse rarely used facets.

## Query correction and synonyms
- Spelling correction: if the original query has zero or very few results and a correction has many, show corrected results with "Search instead for [original]".
- Synonyms: map user vocabulary to content vocabulary (for example "PTO" to "annual leave"). Maintain as a reviewed list, owned by content or search team.
- Best bets: pin a curated destination for high-volume known-item queries ("login", "pricing", "holiday calendar").
- Stemming and plural handling are engine settings; confirm with engineering, do not promise in copy.

## Zero-result layout
1. Heading restating the query: "No results for 'quartely report'".
2. Correction: "Did you mean 'quarterly report'?" as a link that runs the search.
3. Filter recovery: "You have 3 filters on. Remove 'Year: 2019'" (most restrictive first) and "Clear all filters".
4. Scope recovery: "Search all of the site instead of Docs".
5. Popular destinations or categories related to the query.
6. Human fallback: contact, help center or request content.

## Query test set
- Top queries by volume (known-item and navigational).
- Top zero-result queries.
- Queries with high refinement or exit rate.
- Synonym pairs, misspellings, plurals, codes and IDs (order numbers, SKUs).
- Very long queries, single characters, special characters, non-Latin input where relevant.
For each: expected top result, actual top result, pass or fail.

## Metrics to instrument
- Search usage rate, zero-result rate, refinement rate, click-through and click position, exit rate from results, time to first click, filter usage.
- Review zero-result and high-refinement queries on a regular cadence; each review produces synonym, best-bet or content-gap tickets.

## Worked example: Internal knowledge base search

### Before
- Header search icon opens a bare field. Enter opens the first autocomplete item.
- Results page clears the field. Facets: "doc_type", "space_key". Zero results: "No results found."
- Employees search "PTO"; content says "annual leave"; zero results.

### After
- Visible search field in header; empty focus shows recent searches.
- Two labeled groups: "Suggestions" (query completions) and "Pages" (top 3 instant results). Enter runs full search on typed text.
- Results: query in field, "38 results in All spaces", scope chip removable, snippets highlight terms, type badges (Policy, How-to, Form).
- Facets: "Content type", "Team", "Last updated", in usage order with counts.
- Synonym "PTO" to "annual leave"; best bet for "PTO" pins the Leave Policy page.
- Zero results show correction, filter removal, "Search all spaces", popular policies and "Ask HR".

### Filled facet row

| Facet (user label) | Source field | Values and order | Select logic | Counts shown | Default state | Mobile placement |
|---|---|---|---|---|---|---|
| Content type | doc_type | Policy, How-to, Form, Announcement (by usage) | Multi-select, OR within | Yes, disjunctive | Collapsed except on mobile sheet top | Filter sheet, first group |

## Sources
- WAI-ARIA Authoring Practices Guide: combobox pattern, listbox pattern.
- Morville and Rosenfeld, Information Architecture; Morville and Callender, Search Patterns.
- Nielsen Norman Group site search and faceted navigation guidance; Baymard Institute search research; verify current guidance.
