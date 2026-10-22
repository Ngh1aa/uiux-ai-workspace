# Chart Selection and Panel States Reference

Read this when two chart types both seem plausible, when specifying the states of a panel, or when writing the panel inventory. The SKILL.md decision table is the default; this file covers the tie-breakers.

## Tie-breakers between plausible charts

### Bar vs line for time
- Line when the reader cares about shape, slope or turning points across many periods.
- Column bars when there are few discrete periods (for example quarters) and the reader compares individual period values.
- Never connect points with a line when the x axis is categorical and unordered; the line implies continuity.

### Stacked vs grouped bars
- Stacked when the total matters most and one segment (the baseline segment) is the key comparison. Only the bottom segment and the total sit on an aligned scale.
- Grouped (or small multiples) when comparing segments across categories matters more than the total.
- More than about four segments: switch to small multiples.

### Pie or donut vs bar
- Pie or donut is acceptable only for two or three parts of a meaningful whole, where "roughly half" or "about a quarter" is the message.
- If readers must rank or compare similar parts, use a sorted bar. Angle and area rank below length in Cleveland and McGill.

### Small multiples vs one busy chart
- When a line chart has more than a handful of series, highlight the one or two that matter and gray the rest, or split into small multiples with shared axes.
- Shared y axis is the default for small multiples; independent axes must be labeled loudly because they defeat comparison.

### Heatmap vs table
- Heatmap when the pattern (where the hot spots are) is the message.
- Table when exact values are the message. A table with conditional emphasis on a few cells often beats a heatmap.

### Map vs bar
- Use a map only when geography itself explains the data (proximity, region clusters). Otherwise a sorted bar of regions is faster to read and more accessible.
- Choropleths use rates or normalized values; raw counts go on symbol maps.

## Color rules
- Categorical palette: a small set of distinguishable hues; beyond that, group into "Other" or use direct labels.
- Sequential (ordered magnitude): single hue, light to dark, or a perceptually uniform scale.
- Diverging (above or below a meaningful midpoint such as target or zero): two hues with a neutral middle, and the midpoint must be meaningful.
- Semantic status colors (error, warning, success) are reserved for status. Do not reuse the error red as a series color.
- Test under color vision deficiency simulation and in dark mode. Pair status color with icon, text or position.

## Number formatting rules
- Tile: abbreviated, 2 to 3 significant figures (1.24M, 38.2%). Tooltip and table: full value.
- Align numbers right and use tabular figures in tables beside charts.
- Negative values: minus sign or parentheses consistently, per audience convention (finance often uses parentheses).
- Deltas: show sign explicitly (+4.1%), and say whether it is percent change or percentage points.
- Null, zero and "not applicable" are three different states and display differently (for example "No data", "0", "n/a" with an explanation).

## Panel state matrix

| State | Trigger | Display | Must not |
|---|---|---|---|
| Loading | Query in flight | Skeleton of the chart frame with title and axes visible | Block other panels |
| Empty (true zero) | Query returned zero events | Chart with zero values or a "0 in this period" message | Look like an error |
| No data | Source has no rows for this filter | Message naming the filter and a reset action | Show an empty axis without explanation |
| Partial | Some sources failed or period incomplete | Data with a marked incomplete region (for example dashed final segment for current day) | Present partial totals as final |
| Stale | Last refresh older than the panel's freshness SLA | Data plus visible stale badge and last-updated time | Silently show old numbers |
| Error | Query failed | Inline message, retry action, last good timestamp if available | Blank the whole dashboard |
| Permission | User lacks access | Explain the restriction and who grants access | Show a misleading zero |

## Accessible alternatives
- Text summary: one or two sentences stating the answer ("Signups rose 12% week over week, driven by the referral channel").
- Data table: same values as the chart, with proper headers, reachable from the chart.
- For interactive charts, keyboard navigation through series and points, with an accessible name per point (series, x, y, unit).
- Do not rely on the chart's SVG title alone; screen reader users need the summary and the table.

## Worked example: KPI tile and trend panel

### Before
- Tile: "Revenue  $1,243,567.89  ▲ green arrow". No period, no comparison basis, false precision.
- Chart: pie chart of revenue by 9 product lines, legend sorted alphabetically, rainbow colors, no data labels.
- Header: no last-updated time. Pipeline failed overnight; numbers were from two days earlier.

### After
- Tile: "Revenue, Q3 to date: $1.24M (USD). +4.1% vs Q3 last year. Target $1.30M (95%). Updated 08:10 UTC, refreshes hourly." Arrow plus text "+4.1%", color plus sign, so meaning survives without color.
- Chart: horizontal bar of revenue by product line, sorted descending, single hue, top two highlighted with direct labels, remaining grouped as "Other (5 lines)". Value axis starts at zero.
- Title states the answer: "Two product lines make up 61% of Q3 revenue".
- Stale state: when last refresh is older than 2 hours (the panel SLA), the tile shows a stale badge and the last good time.
- Alternative: text summary under the chart plus "View as table" link.

### Filled panel inventory row

| Panel | Question answered | Owner/action | Chart type | Encoding | Units and format | Timeframe and comparison | Freshness SLA | States | Text alternative |
|---|---|---|---|---|---|---|---|---|---|
| Q3 revenue by line | Which product lines drive Q3 revenue? | Sales lead, reallocate promo budget | Sorted horizontal bar | y: line, x: revenue, color: emphasis top 2 | USD, abbreviated on bars, full in tooltip | Q3 to date vs Q3 last year | Hourly, stale after 2 h | Skeleton / "No sales for this filter" + reset / stale badge / inline retry | Summary sentence + table |

## Sources
- Cleveland and McGill (1984) graphical perception.
- Stephen Few, "Information Dashboard Design" and the bullet graph specification.
- Edward Tufte, "The Visual Display of Quantitative Information".
- IBM Carbon data visualization; Material Design data visualization guidance; verify current guidance.
- W3C WAI complex images tutorial and WCAG 1.4.1 and 1.4.11.
