# A49.1 — Lifecycle Contract Reconciliation

Status: **IMPLEMENTED / VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A48 provider-convergence slice

## Purpose

A49.1 maps the two supported top-level execution experiences into one comparison vocabulary **without** merging their runtime APIs.

Current surfaces:

```text
Factory product lifecycle
uiux-factory/run.py
→ CreativeDirectorDevelopmentManager / core/manager/
→ RunContext

Managed Flow lifecycle
skills_UIUX/scripts/uiux-agent.py --managed
→ ManagedFlowController
→ ManagedWebsiteRun
```

Both already share canonical routing/runtime primitives, but they do not expose the same lifecycle semantics.

The executable reconciliation surface is:

```text
core/runtime/lifecycle_reconciliation.py
```

It is descriptive/read-only and has no execution, authority, gate, evidence or release effect.

## Canonical comparison phases

A49.1 uses ten comparison phases:

```text
INTAKE
INTERPRET
PLAN
RESEARCH
DESIGN
IMPLEMENT
QA
REPLAN
FINALIZE
RELEASE
```

These are a comparison vocabulary, **not a new lifecycle engine**.

## Factory profile

Factory is a product-oriented async pipeline.

Important properties:

- `run.py` owns user intake and exclusive run locking;
- manager/orchestration layers own named product/design stages;
- `RunContext` is the top-level product-run state;
- research/design are explicit Factory stages and artifacts;
- implementation can be AI, template or bounded external handoff;
- quality loop owns browser/visual/runtime verification work;
- creative revision can preserve upstream artifacts and invalidate/rerun from the earliest owning stage;
- normal `run.py` completion does **not** expose production deployment as an implicit final step.

Factory design work therefore remains richer than a generic stage-state machine.

## Managed profile

Managed execution is an explicit checkpoint/state-machine lifecycle over the declarative resolved flow.

Important properties:

- `ManagedFlowController.start_from_goal()` interprets the task and bounds authority;
- `FlowPlanner` resolves the canonical declarative flow;
- `ManagedWebsiteRun` stores active stage, revision/replan state and completed stages;
- research/design/implementation/QA are resolved `flow_stage` work rather than hard-coded product-stage methods;
- `start_stage()` / `complete_stage()` advance explicit specialist checkpoints;
- human-marked gates may require explicit approval;
- `replan()` delegates to canonical FlowPlanner bounded replanning;
- terminal evaluation is derived from latest-effective trusted evidence;
- workspace finalization and production release are separate `ProductionReleaseController` actions with explicit authority requirements.

## Key non-parity

A49.1 explicitly records differences instead of pretending equivalence:

1. Factory is one async product pipeline; managed execution exposes explicit resumable/checkpoint stage operations.
2. Factory has named product/design stages; managed design/research/QA are declarative flow stages.
3. Factory normal completion finalizes `RunContext` but does not implicitly deploy production; managed CLI has explicit finalize/release controller actions.
4. Factory creative revision is source-run and earliest-owner aware; managed replanning is signal/flow-revision based.
5. `RunContext` and `ManagedWebsiteRun` are different top-level state schemas.

These are the reasons `adapter_required=true` remains correct.

## Shared invariants

Despite lifecycle shape differences, both surfaces must retain the same governance invariants:

- canonical GoalInterpreter / FlowPlanner remain routing owners;
- provider/model prose is not trusted evidence;
- memory remains advisory and cannot satisfy current-run gates;
- natural language/provider output cannot escalate caller authority;
- run/stage completion is separate from release authority.

## Evidence boundary

Lifecycle mapping must never collapse these concepts:

```text
artifact exists
≠ stage complete
≠ trusted evidence PASS
≠ run complete
≠ workspace finalized
≠ production released
```

A49.1 therefore records an `evidence_contract` and `authority_contract` per phase rather than deriving one synthetic status.

## Executable drift guards

`tests/test_lifecycle_reconciliation_a49.py` protects:

- the same ten comparison phases on both profiles;
- real top-level entrypoint/state-schema differences;
- Factory release remaining `not_exposed` in default product run;
- managed finalize/release remaining separate controller actions;
- audited Factory stage entrypoints still existing;
- audited ManagedFlowController operations still existing;
- reconciliation module remaining descriptive only.

If source entrypoints move, the test should fail and force a reconciliation update rather than silently preserving stale architecture prose.

## Non-goals

A49.1 does not:

- create a unified lifecycle runtime;
- modify `RunContext` or `ManagedWebsiteRun`;
- change Factory manager sequencing;
- change ManagedFlowController transitions;
- change FlowPlanner or stage routing;
- change evidence/gate semantics;
- change finalize/release authority;
- migrate provider defaults;
- claim that Factory and managed lifecycle are behaviorally equivalent.

## Acceptance criteria

A49.1 is complete when:

- [x] both top-level lifecycle surfaces are represented by immutable read-only profiles;
- [x] all ten comparison phases are covered;
- [x] each phase records owner, entrypoints, input/output, evidence, authority and side effects;
- [x] known non-parity is explicit;
- [x] shared truth/authority invariants are explicit;
- [x] source drift tests protect audited entrypoints;
- [x] reconciliation has no execution/gate/evidence/release effect;
- [ ] final head passes UIUX Factory CI;
- [ ] final head passes A20 regression/security/dogfood;
- [ ] PR is mergeable.

## Handoff

After A49.1 is green and merged, A49.2/A49.3 may be combined into one **Lifecycle Adapter + Parity** package if the implementation remains adapter-first.

That package should introduce a shared lifecycle event/status projection over the two existing state owners, then compare equivalent runs. It must not introduce a third state machine or change release authority as part of the adapter work.
