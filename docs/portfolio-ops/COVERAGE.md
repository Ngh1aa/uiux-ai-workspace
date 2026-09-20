# Portfolio Coverage Matrix

Scoring rule: **no repository evidence = 0**. This matrix is intentionally conservative and must only increase when an artifact plus appropriate verification exists.

| Area | Score | Evidence / state |
|---|---:|---|
| Product & UX strategy | 0/5 | UNKNOWN — no active portfolio project is currently tracked in this repository. |
| Research & validation | 0/5 | UNKNOWN — no project research/validation artifact is available under the current repository structure. |
| Information architecture & user flows | 0/5 | UNKNOWN — no active project artifact is available to score. |
| Visual/UI craft | 0/5 | UNKNOWN — no rendered project evidence is available to score. |
| Design system | 0/5 | UNKNOWN — no active project artifact is available to score. |
| Interaction & motion | 0/5 | UNKNOWN — Factory capability is not portfolio-project evidence. |
| Accessibility | 0/5 | UNKNOWN — QA tooling is not evidence that a portfolio project passed WCAG-related gates. |
| Responsive & multi-platform | 0/5 | UNKNOWN — no 375/768/1440 project evidence is available to score. |
| UX writing & content | 0/5 | UNKNOWN — no active project artifact is available to score. |
| Complex domain | 0/5 | UNKNOWN — no active project artifact is available to score. |

## Hard-gate rule

Console errors, missing visible focus, contrast failure, or broken layout at any required viewport prevent DONE regardless of aggregate score.

## Evidence boundary

`uiux-factory/` contains tooling and verification capabilities. Per `README.md`, the old standalone `showcase/` has been removed. Tooling capability must not be counted as proof that a portfolio project itself has passed product, visual, accessibility, responsive, or validation gates.
