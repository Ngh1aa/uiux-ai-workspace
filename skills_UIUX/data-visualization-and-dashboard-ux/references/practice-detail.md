# Thực hành chuyên sâu

Chỉ mở khi cần chi tiết trong mục dưới đây; WORKFLOWS.md vẫn là nguồn định tuyến duy nhất.

# Data Visualization & Dashboard UX

## Goal and scope

Every chart on the screen earns its place by answering a named question that leads to a decision or an action. A dashboard is a ranked list of answers, not a wall of widgets. The output is a spec where each panel states its question, encoding, units, timeframe, freshness and fallback states, so engineering cannot ship an ambiguous number.

**When not to use**

- Row-level records the user scans, sorts, selects or edits: use [data-tables-and-enterprise-ux](../../data-tables-and-enterprise-ux/SKILL.md). A dashboard can link into a table, but the table is a different design problem.
- Defining which metrics matter and how they are instrumented: use outcome-metrics-and-instrumentation first, then come back here to display them.
- Interpreting A/B results or statistical significance: use experimentation-interpretation.
- Status of a running job or multi-step process: use [complex-workflow-and-progress-ux](../../interaction-patterns-and-form-ux/references/complex-workflow-and-progress-ux/README.md).
- Generic loading, empty and error patterns beyond charts: use [state-feedback-and-error-recovery](../../state-feedback-and-error-recovery/SKILL.md).

## Decisions

**1. Dashboard type decides layout**
- **Operational (monitoring)**: refreshed often, scanned in seconds, answers "is anything wrong right now?". Lead with exceptions and thresholds, keep it to one screen, no exploration chrome.
- **Analytical (exploration)**: answers "why?". Needs filters, drill-down, comparison periods and the overview, then zoom and filter, then details on demand pattern (Shneiderman).
- **Strategic (reporting)**: weekly or monthly cadence, few KPIs with targets and trend context. Annotate events that explain changes.
- If stakeholders want one dashboard to do all three, split it. Mixing cadences is the most common cause of unreadable dashboards.

**2. KPI hierarchy before chart type**
- Rank questions by actionability: what changes someone's behavior today sits top-left (in LTR reading order), context sits below.
- A KPI tile always carries: value, unit, comparison (vs target or vs prior period, with the period named), direction meaning (is up good?), and freshness.
- Cap the top KPI row at the number of things the audience can act on. If a tile has no owner or no action, demote it.

**3. Chart type follows the analytical task**
| Task | Default | Acceptable | Avoid |
|---|---|---|---|
| Compare categories | Horizontal bar (sorted) | Dot plot, lollipop | Pie with many slices, 3D bars |
| Trend over time | Line | Area (single series), column for few discrete periods | Pie per period, dual unrelated axes |
| Part to whole | Stacked bar 100%, single bar | Pie or donut with 2 to 3 parts | Pie with near-equal slices |
| Distribution | Histogram, box plot | Strip or violin for analysts | Average-only bar |
| Relationship | Scatter | Connected scatter, heatmap for dense pairs | Dual-axis line implying correlation |
| Deviation from target | Bullet chart, diverging bar | Line with target band | Gauge or speedometer |
| Geographic | Choropleth (normalized rates) | Symbol map for counts | Choropleth of raw counts |
| Single status | Number plus delta plus sparkline | Bullet chart | Decorative gauge |

**4. Encoding ranking (Cleveland and McGill)**
Order of accuracy for quantitative judgment: position on a common scale, position on non-aligned scales, length, direction (slope) and angle, area, volume and curvature, shading and color saturation. Hue is not on this quantitative ranking; use it for categories. Rules that follow:
- Put the most important comparison on a shared aligned axis.
- Bars encode length, so the value axis starts at zero. Lines encode slope, so a non-zero baseline is allowed when labeled.
- Color is for categories (a small set of hues) or one emphasis. Never the only channel for meaning: pair with labels, position, shape or pattern (WCAG 1.4.1 Use of Color).
- Direct labels beat legends when there are few series.

**5. Numbers, units and freshness**
- Format by magnitude and audience: abbreviate large values (1.2M) on tiles, show full precision in tooltips and tables.
- Keep decimals consistent within a column or axis; do not show precision the data does not have.
- Units on every axis or tile (currency, %, ms, count). Percent vs percentage point is stated explicitly for deltas.
- Timeframe and timezone visible ("Last 7 days, UTC"). Comparison period named, not "vs previous".
- Freshness: show "Updated 5 min ago" and the expected refresh cadence. When data is older than its cadence, the panel enters a visible stale state instead of quietly showing old numbers.
- Locale-aware number and date formatting; see [localization-and-i18n](../../localization-and-i18n/SKILL.md).

**6. Interaction**
- Tooltips supplement, never hold the only copy of a critical value; touch and keyboard users must reach the same information.
- Cross-filtering must show which filter is active and offer a single reset.
- Drill-down keeps a breadcrumb back to the overview and preserves filter state.

**7. Accessibility**
- Each chart has a text summary (the answer to its question) plus a data table alternative for important data.
- Interactive charts are reachable by keyboard with visible focus; series and points expose accessible names.
- Contrast for marks and gridlines is checked against WCAG non-text contrast (1.4.11); verify current guidance.

## Workflow

1. Define audience, decision and monitoring cadence, and classify the dashboard type (Decision 1).
2. Establish KPI hierarchy before chart type: list questions, rank by actionability, assign owners.
3. Match visualization to comparison, trend, distribution, part to whole, deviation or relationship task (Decision 3), and pick encodings by the ranking in Decision 4.
4. Use overview, then filter and zoom, then details when exploration is needed; define drill paths and filter persistence.
5. Show units, timeframe, timezone, freshness and source or context on every panel.
6. Provide accessible text summary and table alternatives for important data.
7. Design loading, no-data, partial-data, stale-data and error states per panel, so one failing query does not blank the whole dashboard.
8. Validate with real data extremes (zero, null, outliers, very long labels, one category dominating).

Read [chart selection and states reference](../references/chart-selection-and-states.md) when choosing between two plausible chart types, specifying panel states, or writing the panel spec. It includes a worked before/after example.
Before handoff run [dashboard gate](../checklists/dashboard-gate.md).

**Anti-patterns**

- KPI tiles with a big number and a green arrow but no comparison period, so nobody knows "up vs what".
- Pie or donut charts with 7 or more slices, or slices sorted alphabetically.
- Truncated bar axes that turn a 2% difference into a visual doubling.
- Dual-axis line charts with independently scaled axes that suggest correlation.
- Red/green as the only status signal, unreadable for many color vision deficient users.
- Gauges and speedometers taking a quarter of the screen to show one number.
- Rainbow sequential palettes for ordered data; use a single-hue or perceptually uniform sequential scale.
- Choropleths of raw counts that just map population.
- "Last updated" missing, so a broken pipeline shows yesterday's numbers as current.
- A single spinner over the whole dashboard while one slow panel loads.
- Chart titles that name the metric ("Revenue") instead of the answer or question ("Revenue is 8% below target this quarter").

**Output**

A dashboard spec with:
1. Audience, decision, cadence and dashboard type.
2. Panel inventory table:

| Panel | Question answered | Owner/action | Chart type | Encoding (x / y / color) | Units and format | Timeframe and comparison | Freshness SLA | States (loading / empty / stale / error) | Text alternative |
|---|---|---|---|---|---|---|---|---|---|

3. Layout order with rationale (actionability ranking).
4. Interaction spec: filters, cross-filter, drill path, reset.
5. Accessibility notes per panel.

## Quality gate

- PASS only if every visualization answers a named question written in the spec.
- PASS only if color is not the sole encoding of any meaning.
- PASS only if units, timeframe and comparison period are explicit on every panel.
- PASS only if dashboard order follows the actionability ranking.
- PASS only if every bar or area chart value axis starts at zero, or the exception is documented.
- PASS only if each panel has defined loading, empty, stale and error states, and stale data is visibly marked.
- PASS only if important charts have a text summary and data table alternative.
- FAIL if any KPI shows a delta without naming its comparison basis.

**Baseline / sources**

- Cleveland and McGill, graphical perception ranking (1984).
- Stephen Few, dashboard design and bullet graph; Edward Tufte, data-ink and chart integrity.
- Shneiderman, visual information-seeking mantra.
- IBM Carbon data visualization guidelines; Material Design data visualization guidance.
- W3C WCAG 2.x (1.1.1, 1.4.1, 1.4.11) and WAI tutorials on complex images; verify current guidance.
