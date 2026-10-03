# P1.4 — Multi-Intent / Multi-Surface Routing

## Purpose

P1.4 prevents a prompt with several explicit work owners from being collapsed into one `intent` + one `change_surface`.

Examples:

- `audit → redesign → implement → QA`
- `fix hero + redesign checkout`
- `fix CTA button + redesign checkout + keep animation unchanged`

## Architecture

P1.4 is a non-breaking envelope above Task Contract v1.0.

1. `GoalInterpreter` still owns canonical domain/archetype/features/constraints/ambiguity.
2. `WorkSequenceInterpreter` detects explicit actionable clauses.
3. `WorkSequenceContract` keeps the canonical profile and ordered `WorkSegment` items.
4. `SequenceFlowPlanner` sends every segment back through the existing canonical `FlowPlanner`.
5. Each segment therefore keeps smallest-credible-flow behavior instead of introducing a new mega-flow.

A work segment records:

- lifecycle `phase` (`audit`, `design`, `implementation`, `qa`),
- canonical routing `intent`,
- local `scope`,
- local `change_surface`,
- source text,
- inheritance owner for pronoun/bare lifecycle steps,
- global preserve/forbidden constraints.

## Inheritance

Bare lifecycle clauses such as `implement it` or `QA it` inherit the nearest previous change owner. An initial object-less audit can forward-inherit the next explicit design target.

This inheritance is structural only. It does not invent domain truth or bypass P1.3 ambiguity checks.

## Execution boundary

`ProfessionalWebsiteFlow.resolve()` remains the single-work API. If the goal is an explicit sequence it raises `MultiSurfaceRoutingError` rather than silently choosing one surface.

Use `resolve_work_plan()` for a sequence. Each work segment receives its own canonical flow and an active stage:

- `audit` → research stage
- `design` → design stage, or implementation for focused/micro flows with no separate design stage
- `implementation` → implementation stage
- `qa` → QA stage

Factory stage skill resolution is sequence-aware and only aggregates segments active for the requested lifecycle stage.

## Compatibility boundaries

- P1.1 specialist composition is unchanged and runs independently for each segment flow.
- P1.2 explicit mixed-domain ownership remains authoritative.
- P1.3 unresolved domain ambiguity still blocks sequence planning until target-project truth or explicit ownership exists.
- Task Contract v1.0 remains intact; P1.4 uses Work Sequence Contract v1.0 as an envelope.
- Single-action prompts remain on the original single-flow path.

## Stress corpus

The P1.4 matrix covers:

- lifecycle chains,
- mixed `MICRO` / `FOCUSED` / `PAGE` / `REDESIGN` / `PRODUCT` owners,
- constraint inheritance,
- English and Vietnamese phrasing,
- comma, conjunction and arrow separators,
- no-design audit/QA and implementation/QA chains,
- single-task controls to guard against over-segmentation.

The dedicated CI lane produces JSON evidence and the Routing Intelligence Contract includes the focused P1.4 test suite.
