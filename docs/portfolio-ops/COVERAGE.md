# Portfolio Coverage Matrix

Evidence policy: score is `0` unless a repository artifact or verified QA evidence supports a higher score. This bootstrap intentionally does **not** infer portfolio quality from the existence of Factory capabilities.

| Area | Score | Evidence state | Evidence |
|---|---:|---|---|
| Product & UX strategy | 0/5 | UNKNOWN | No selected portfolio-project artifact has been evaluated yet. |
| Research & validation | 0/5 | UNKNOWN | No selected portfolio-project research/validation artifact has been evaluated yet. |
| Information architecture & user flows | 0/5 | UNKNOWN | No selected portfolio-project IA/flow artifact has been evaluated yet. |
| Visual/UI craft | 0/5 | UNKNOWN | No rendered portfolio-project evidence has been evaluated yet. |
| Design system | 0/5 | UNKNOWN | No selected portfolio-project token/component artifact has been evaluated yet. |
| Interaction & motion | 0/5 | UNKNOWN | No selected portfolio-project interaction evidence has been evaluated yet. |
| Accessibility | 0/5 | UNKNOWN | No target-project WCAG/browser evidence has been evaluated yet. |
| Responsive & multi-platform | 0/5 | UNKNOWN | No target-project 375/768/1440 evidence has been evaluated yet. |
| UX writing & content | 0/5 | UNKNOWN | No selected portfolio-project content-stress evidence has been evaluated yet. |
| Complex domain | 0/5 | UNKNOWN | No selected portfolio-project domain evidence has been evaluated yet. |

## Important distinction

`uiux-factory/` contains capabilities for design reasoning and QA, but those capabilities are not evidence that a portfolio project itself satisfies the matrix. Scores will rise only when project-specific artifacts and verification are inspected.

## Next evidence pass

Continue on the current `auto/*` branch and inventory only project-specific artifacts that are actually present and attributable. Preserve `UNKNOWN`/0 where evidence is absent. Hard gates must not be averaged away.
