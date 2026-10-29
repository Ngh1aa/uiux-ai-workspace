# Thực hành chuyên sâu

Chỉ mở khi cần chi tiết trong mục dưới đây; WORKFLOWS.md vẫn là nguồn định tuyến duy nhất.

# Site Search & Findability

## Goal and scope

Users who know roughly what they want get to it in one query or one refinement, and users who fail get a recovery path instead of a dead end. Search is designed from real query logs and vocabulary, scoped so results are predictable, and instrumented so the team can see where it fails.

**When not to use**

- Navigation structure, labels and menus (findability by browsing): use [information-architecture](../../information-architecture/SKILL.md); validate with card-sorting-and-tree-testing.
- Ranking in external search engines and content for organic traffic: use seo-strategy or search-demand-and-content-briefing.
- Filtering and sorting inside a single admin table: use [data-tables-and-enterprise-ux](../../data-tables-and-enterprise-ux/SKILL.md).
- Product listing pages and merchandising specifics: compose with [ecommerce-website](../../industry-playbooks/references/ecommerce-website.md).
- Conversational or AI answer search: compose with [human-ai-interaction-design](../../human-ai-interaction-design/SKILL.md).

## Decisions

**1. Intent model first**
- Classify top queries: known-item (exact page or product), exploratory (topic), navigational (a section such as "pricing" or "login"), and help or task ("reset password").
- Known-item and navigational intents get best-bet results (curated, pinned at top). Exploratory intents get facets and topic grouping.
- Mine vocabulary from logs, support tickets and interviews; build a synonym list (user term to content term) before tuning ranking.

**2. Entry point and scope**
- Search box visible (not icon only) on content-heavy sites where search is a primary path; icon-to-expand is acceptable on small screens or when search is secondary.
- Default scope is the whole site. Scoped search (within docs, within this section) is shown as a visible, removable scope chip or selector, never hidden state.
- If multiple corpora exist (products, articles, people), use one query with tabbed or grouped results rather than separate search boxes.
- On mobile, search opens as a full-screen layer with the field focused, recent searches and a clear way back.

**3. Autocomplete vs suggestions**
- **Query suggestions (autosuggest)**: complete the query text; selecting runs a search. Use when queries are varied and users benefit from vocabulary help.
- **Instant results (autocomplete to destinations)**: show matching items that navigate directly. Use for known-item lookups (people, products, pages).
- Both can coexist in separate labeled groups. Pressing Enter always runs a full search on the typed text; suggestions never block it.
- Show recent searches on focus when the field is empty; let users remove them.
- Highlight the completed part, not the typed part, so users see what is added. Keep the list short and relevant; no suggestions is better than bad ones.
- Implement with the WAI-ARIA APG combobox pattern: input with `role="combobox"`, `aria-expanded`, `aria-controls` the listbox, `aria-activedescendant` for the highlighted option, arrow keys move, Enter selects, Escape closes and keeps text.

**4. Results page**
- Query stays visible and editable in the field at the top; result count and active scope are stated.
- Result item shows title, type, context (section, breadcrumb or date), and a snippet with query terms highlighted. Type badges when corpora are mixed.
- Default sort is relevance; offer sorts users actually use (newest, price). State the active sort.
- Corrected queries: "Showing results for X. Search instead for Y." Never silently replace the user's query.
- Preserve the query, filters and scroll on back navigation; put them in the URL.

**5. Faceting**
- Facets reflect user criteria found in research, in user language, ordered by usage.
- Show counts per facet value; hide or disable zero-count values consistently.
- Multi-select within a facet is OR; across facets is AND. Make this visible through grouping.
- Active filters appear as removable chips with "Clear all". On mobile, filters live in a sheet with an "Apply" that shows the resulting count, or apply live with a count, chosen once per product.
- Long value lists get a "Show more" and a filter-within-filter search.

**6. Zero results and poor results**
- Never a blank page. Show: the query, spelling correction or "Did you mean", the option to remove filters (naming which), broadened scope, popular or related destinations, and a contact or browse fallback.
- If filters caused zero results, say so and offer one-click removal of the most restrictive filter.
- Log every zero-result query; review regularly and fix via synonyms, content gaps or best bets.

**7. Instrumentation**
- Track queries, zero-result rate, refinement rate, click-through position, exits from results and time to first click. Define targets in outcome-metrics-and-instrumentation.
- Respect privacy: do not log personal data typed into search beyond policy.

## Workflow

1. Model search intents, common vocabulary and high-value destinations from logs and research (Decision 1).
2. Define search entry point, scope and mobile behavior (Decision 2).
3. Design autocomplete and suggestions without preventing full search; specify the combobox interaction (Decision 3).
4. Keep query visible and editable on results; define result anatomy, sort and correction behavior (Decision 4).
5. Design result hierarchy, filters and sorting around user criteria (Decision 5).
6. Handle typo, synonym, no-result and refinement paths (Decision 6).
7. Instrument query, zero-result and refinement behavior and set a review cadence (Decision 7).
8. Test with real top queries and top failing queries, including keyboard and screen reader passes.

Read [search patterns reference](../references/search-patterns.md) when specifying combobox keyboard behavior, facet logic, zero-result layouts, the query test set, or when you need a worked example.
Before handoff run [search gate](../checklists/search-gate.md).

**Anti-patterns**

- Search icon that opens a field with no recent searches, no suggestions and no visible scope on a docs site where search is the main path.
- Autocomplete that hijacks Enter to open the first suggestion instead of searching the typed query.
- Silent auto-correction that replaces a valid but rare term.
- Results page that clears the query field, so users retype to refine.
- Facets named after database fields ("cat_id", "Taxonomy 2").
- Zero-count facet values that lead to empty pages.
- "No results found." with nothing else on the page.
- Separate search boxes for blog, docs and store with different behavior.
- Filters that reset on back navigation from a result.
- Suggestion dropdown not reachable by keyboard, or that steals focus from the input.

**Output**

1. Intent and vocabulary table (top queries by intent, synonyms, best bets).
2. Entry and scope spec, including mobile layer.
3. Autocomplete spec: groups (recent, suggestions, instant results), limits, keyboard map, ARIA roles.
4. Results spec: item anatomy, sort, correction copy, URL state.
5. Facet table:

| Facet (user label) | Source field | Values and order | Select logic | Counts shown | Default state | Mobile placement |
|---|---|---|---|---|---|---|

6. Zero-result and low-result recovery layout with copy.
7. Instrumentation plan and review cadence.

## Quality gate

- PASS only if search supports the primary retrieval jobs, verified with the top real queries.
- PASS only if zero results always provide recovery (correction, filter removal, related destinations).
- PASS only if filter names use user language from research, not schema names.
- PASS only if suggestion and result interactions are keyboard and focus usable per the APG combobox pattern.
- PASS only if Enter always runs a full search on the typed text.
- PASS only if the query remains visible and editable on the results page, and query, filters and sort persist in the URL.
- PASS only if active scope and filters are visible and removable.
- PASS only if zero-result queries are logged and reviewed on a defined cadence.

**Baseline / sources**

- WAI-ARIA Authoring Practices: combobox pattern and listbox.
- Peter Morville and Louis Rosenfeld, Information Architecture; Morville and Callender, Search Patterns.
- Nielsen Norman Group guidance on site search, autocomplete and faceted navigation (no figures assumed).
- Baymard Institute research on ecommerce search and filtering; verify current guidance.
- Material Design search pattern; IBM Carbon search component.
