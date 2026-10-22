# Governance Operations Reference

Read when you are setting up the contribution process, writing a deprecation notice, defining adoption metrics or preparing a system health report. The main skill holds the decision rules; this file holds templates, metric definitions and a worked example.

## 1. Adoption and health metrics

Define each metric with its source so it can be recomputed. Do not report a metric you cannot measure repeatably.

| Metric | Definition | Typical source | Why it matters |
|---|---|---|---|
| Product adoption | Share of consuming products on a supported major version | Package manifests across repos | Shows reach and upgrade lag |
| Component coverage | Share of UI elements in a product rendered by system components | Static import analysis, or Figma library analytics for design files | Shows real use, not installs |
| Version lag | Number of majors or minors each product is behind | Lockfiles | Predicts migration cost |
| Exception rate | Count of documented overrides, detached instances and local re-implementations per product | Lint rules, code search, library analytics | Shows where the system fails needs |
| Hardcoded value count | Raw colors, spacing and type values not from tokens | Lint or style audit | Token drift signal |
| A11y status | Share of stable components with a passing review in the last review cycle | Status table | Quality of the system itself |
| Contribution throughput | Requests triaged within service level; median time to decision | Issue tracker | Predicts forking |
| Deprecated usage | Remaining call sites of deprecated APIs per product | Code search, runtime warnings | Gate for removal |

Never use component count, docs page views or Figma insert counts alone as health.

## 2. Gap analysis template

```
Request: <need in user terms>
Requesting product(s): <names>
Nearest existing components:
  1. <component> fails because <specific gap>
  2. <component> fails because <specific gap>
Can a variant, prop, slot or token solve it? <yes/no, why>
Second consumer identified? <product or roadmap item>
Decision: use existing | extend | local composition | new component | local experiment
Review date (if experiment): <date>
```

## 3. Change classification quick table

| Change | Semver | Notes |
|---|---|---|
| Add optional prop or variant | Minor | Default must preserve current behavior |
| Add token | Minor | Name by meaning |
| Fix focus ring missing on one state | Patch | Even if visually noticeable |
| Change default size from md to sm | Major | Changes existing rendering |
| Rename prop, keep old as alias with warning | Minor | Old alias removed in a later major |
| Remove alias | Major | Only after window and zero tracked usage |
| Token value change, same meaning (tuned gray) | Minor or patch per policy | Run visual regression on consumers |
| Token value change, new meaning | Major | Better: new token, deprecate the old |
| Figma variant property rename | Treat as major | Breaks instance overrides |

## 4. Deprecation timeline template

| Stage | Release | What happens | Who acts |
|---|---|---|---|
| Announce | vX.Y (minor) | Deprecated label in code, library and docs; replacement named; migration guide or codemod published | System team |
| Warn | vX.Y to last minor of X | Console or lint warning in development builds; usage tracked per product | Consumers migrate |
| Check | Before vX+1 | Deprecated usage report; owners of remaining usage contacted | System team and product owners |
| Remove | vX+1.0 (major) | API removed; changelog lists removal with migration link | System team |

Publish the minimum window as policy and apply it every time. Exceptions (security, legal) are documented in the changelog.

## 5. Lightweight RFC template for new or breaking work

```
Title:
Problem (with evidence from at least one product):
Proposal (API, anatomy, tokens):
Alternatives considered (including do nothing):
Accessibility notes (keyboard, screen reader, WCAG 2.2 SC touched):
Breaking? (semver impact and migration plan):
Consumers affected:
Decision and date:
```

## 6. Worked example: duplicate modal components across three products

**Before**

- System ships `Modal`. Product A built `Dialog` with a sticky footer. Product B copied `Modal` into its repo to change padding. Product C uses `Modal` but overrides internal classes for full-screen mobile.
- `Modal` has no focus return to trigger; known bug for months.
- Health report: "42 components, 1,200 Figma inserts this month."

**After**

- Gap analysis: needs are sticky footer (A), compact density (B), full-screen at small viewports (C). None needs a new component.
- `Modal` 4.3.0 (minor): adds `footer` slot with sticky option, `density` token hook, `fullScreenBelow` prop. Focus return fixed in 4.3.1 (patch).
- Product A `Dialog` marked as a local duplicate; migration guide written; product team owns removal by an agreed date.
- Product B fork replaced by `density="compact"`.
- Product C override removed; uses `fullScreenBelow="sm"`.
- `Modal` prop `wide` renamed to `size="lg"`: old prop kept as alias with warning in 4.3.0, removed in 5.0.0 after the deprecation window and zero tracked usage.

**Filled status row**

| Component | Status | Owner | Current version | A11y review (date, result) | Test coverage (unit/visual/a11y) | Consumers | Open exceptions | Deprecation and replacement |
|---|---|---|---|---|---|---|---|---|
| Modal | Stable | Core UI team | 4.3.1 | Last cycle, pass after focus-return fix | Unit yes / visual yes / axe plus manual SR yes | A, B, C | A: local Dialog pending migration | Prop `wide` deprecated in 4.3.0, use `size="lg"`, removal in 5.0.0 |

## 7. Health report outline

1. Adoption by product and version lag.
2. Exceptions: top recurring overrides and what system change would remove them.
3. Accessibility: stable components without a current review.
4. Contribution: requests received, decided, median time to decision.
5. Deprecations: remaining usage before the next major.
6. Decisions needed from leadership (funding, policy, priority).
