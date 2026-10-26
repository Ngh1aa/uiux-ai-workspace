# UX artifact templates

Copy into the target project's `docs/ux/` and fill in. Keep evidence labels honest:
`EVIDENCED` (with source/ID), `HYPOTHESIS`, `UNKNOWN`. Never write invented quotes or participant counts.

| Phase | Template | Owner skill | Use when |
|---|---|---|---|
| U0 Frame | [problem-statement.md](problem-statement.md) | `ux-structure-and-flow-design` | Any new product, feature or redesign |
| U0 Frame | [assumption-map.md](assumption-map.md) | `ux-structure-and-flow-design` | Before committing scope; to pick what to test first |
| U1 Understand | [proto-persona.md](proto-persona.md) | `audience-intent-and-top-tasks` | Audience is known only by team belief |
| U1 Understand | [jtbd-and-top-tasks.md](jtbd-and-top-tasks.md) | `audience-intent-and-top-tasks` | Deciding what the structure must serve |
| U2 Structure | [user-flow.md](user-flow.md) | `ux-structure-and-flow-design` | Every top task |
| U2 Structure | [task-flow.md](task-flow.md) | `ux-structure-and-flow-design` | Dense screens with several steps inside |
| U3 Structure | [ia-sitemap.md](ia-sitemap.md) | `information-architecture` | Navigation and labels |
| U4 Structure | [wireframe-spec.md](wireframe-spec.md) | `ux-structure-and-flow-design` | Key screens before visual design |
| U5 Validate | [heuristic-evaluation.md](heuristic-evaluation.md) | `ux-laws-and-heuristics` | Expert review of wireframes or live UI |
| U5 Validate | [usability-test-plan.md](usability-test-plan.md) | (ngoài phạm vi repo) | Testing with real people |
| U6 Decide | [design-rationale.md](design-rationale.md) | `design-critique-and-rationale` | Any consequential design choice |
| U7 Measure | [ux-scorecard.md](ux-scorecard.md) | `design-critique-and-rationale` | Before/after comparison, release review |
| U1 to V1 | [design-principles.md](design-principles.md) | `experience-principles-and-signature-moments` | After top tasks; principles that settle arguments |
| V1 Handoff | [visual-brief.md](visual-brief.md) | `ux-structure-and-flow-design` → `visual-design-direction` | After UX Readiness passes, before visual exploration |
| V2 Direction | [direction-approval.md](direction-approval.md) | `visual-design-direction` | M and up: 2–3 directions on the key screen, before building the rest |

Order of use for a new product: problem statement → assumption map → proto-persona →
JTBD/top tasks → user flows → IA → wireframe spec → heuristic evaluation →
UX readiness gate → design principles + visual brief → direction approval → (visual design) → usability test plan → design rationale → scorecard.

The steps per job size live in [`WORKFLOWS.md`](../../../WORKFLOWS.md).

