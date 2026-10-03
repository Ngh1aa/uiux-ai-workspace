# P1.5 — Stateful Work-Plan Execution

## Purpose

P1.5 changes the Factory boundary from only understanding an ordered multi-work prompt to knowing which segment is allowed to run, what evidence it consumes, what it must produce, and when the work plan is complete.

P1.5 does **not** replace P1.1–P1.4 routing. It sits after `ResolvedWorkPlan`.

## Execution contract

A resolved P1.4 sequence becomes a `WorkExecutionPlan` with deterministic nodes.

Each node records:

- `segment_id`, lifecycle phase, scope and change surface,
- `depends_on`,
- structural owner inherited from P1.4,
- `preserve` and `forbidden` runtime invariants,
- `required_artifact_kinds`,
- `expected_output_kinds`,
- state: `pending`, `runnable`, `running`, `passed`, `failed`, or `blocked`,
- blocking reason and attempt count.

The default graph is deliberately conservative and ordered: each explicit work segment depends on the preceding segment. This preserves the user's declared work order and can be relaxed by a later parallelism phase without changing the state model.

## Lifecycle artifacts

Default required outputs are:

- audit → `audit-findings`
- design → `design-spec`
- implementation → `implementation-artifact`
- QA → `qa-evidence`

A QA segment that carries `preserve` or `forbidden` constraints must also produce `constraint-evidence` before it can pass.

Artifact references retain producer provenance, optional URI/digest and metadata. Downstream segments only become runnable after dependencies pass and their required artifact kinds are available from direct upstream producers.

## State gates

Initial state:

- first node → `runnable`
- later nodes → `pending`

Transitions:

1. `runnable → running` through `start()`
2. `running → passed` only when all expected outputs are present
3. `running|runnable → failed` through `fail_segment()`
4. downstream nodes become `blocked` when a dependency fails or is blocked
5. a passed dependency with complete artifacts unlocks the next node as `runnable`

The plan is `completed` only when every node is `passed`.

## Resume and partial rerun

`WorkExecutionPlan.to_dict()` persists deterministic state and artifact provenance. `from_dict()` restores it.

`reset_from(segment_id)` invalidates only that segment and descendants:

- upstream passed nodes remain passed,
- upstream artifacts remain available,
- affected artifacts are removed,
- the selected node becomes runnable again once its dependencies and inputs remain valid.

This enables QA-only reruns and repair loops without repeating successful audit/design/implementation work.

## Factory adapter

`ProfessionalWebsiteFlow.resolve_execution_plan(goal, target_truth=None)` is the canonical Factory entrypoint for P1.5.

It performs:

`GoalInterpreter → WorkSequenceInterpreter → SequenceFlowPlanner → WorkExecutionPlan`

Therefore:

- P1.1 specialist composition still occurs inside each segment flow,
- P1.2 explicit mixed-domain ownership remains authoritative,
- P1.3 unresolved ambiguity still fails closed before execution state exists,
- P1.4 still owns decomposition and smallest-credible-flow selection.

## Safety boundary

P1.5 is an execution **state contract**, not an autonomous shell/agent runner. It decides which work is eligible to run and which evidence is required. The caller remains responsible for doing the actual design/code/QA work and recording the resulting artifact references.

## CI evidence

The dedicated P1.5 workflow validates:

- dependency order,
- artifact handoff,
- completion gates,
- wrong-producer rejection,
- failure cascade,
- partial rerun,
- serialization/resume,
- constraint evidence,
- repair-loop ordering,
- P1.3 target-truth compatibility.

The P1.5 test suite is also part of the Routing Intelligence Contract so routing and execution cannot drift independently.
