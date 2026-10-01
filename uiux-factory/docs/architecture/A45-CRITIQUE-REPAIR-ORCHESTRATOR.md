# A45.1 — Critique → Repair Proposal Orchestrator

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A41 critique/repair contracts + A44 critics

## 1. Purpose

A45.1 connects unresolved A44 critique observations to the existing A41 repair contracts without creating an auto-fix agent.

Canonical implementation:

```text
core/brain_os/repair_orchestrator.py
```

For each unresolved `CritiqueIssue`, the orchestrator can propose:

```text
CritiqueIssue
→ RootCause(PROPOSED)
→ RepairDirective(PROPOSED)
→ RetestRequirement(PENDING)
→ RepairLink
```

The output is a `RepairProposalBundle`.

## 2. What the orchestrator may do

It may:

- create deterministic IDs for proposal lineage;
- copy existing canonical evidence references already attached to the source issue into the proposed cause/directive;
- choose a bounded target stage from critic identity;
- define a conservative retest evidence type set;
- preserve source issue severity as repair priority;
- require explicit human approval for P0 repair directives;
- deduplicate repeated issue IDs;
- skip already RESOLVED issues in batch proposal mode.

## 3. What it must not do

It does not:

- execute a repair;
- write target-product code;
- call provider/runtime tools;
- ACCEPT a `RepairDirective`;
- mark a `RetestRequirement` PASSED/FAILED;
- change a `CritiqueIssue` to RESOLVED;
- run canonical gate evaluation;
- create or upgrade trusted evidence;
- merge, deploy or release.

Every bundle declares:

```text
advisory_only = true
execution_effect = none
acceptance_effect = none
resolution_effect = none
gate_effect = none
evidence_effect = none
```

## 4. Proposal semantics

### RootCause

A root cause starts as:

```text
status = PROPOSED
```

Its statement explicitly says that the cause is proposed. Confidence is deliberately bounded below confirmation-level certainty.

### RepairDirective

A directive starts as:

```text
status = PROPOSED
```

It instructs the downstream owner to address the observed issue while preserving source constraints and avoiding scope expansion without authority.

P0 directives set:

```text
requires_human_approval = true
```

This requirement does not itself accept the directive.

### RetestRequirement

A retest starts as:

```text
status = PENDING
evidence_refs = []
```

The orchestrator never fabricates retest evidence.

The acceptance criteria explicitly require canonical evidence before the source issue may be changed to RESOLVED.

## 5. Bounded critic → stage mapping

Current deterministic mapping:

```text
visual         → visual_composition
ux_ia          → ux_strategy
design_system  → design_system
accessibility  → qa
product        → product_strategy
runtime        → qa
evidence_truth → qa
unknown        → qa
```

This is proposal routing only. It does not replace FlowPlanner or execute a Flow stage.

## 6. Bounded retest evidence mapping

```text
visual         → browser_render
ux_ia          → browser_render
design_system  → validator_result
accessibility  → validator_result + browser_render
product        → artifact
runtime        → validator_result
evidence_truth → validator_result
unknown        → validator_result
```

These are proposal requirements for the A41 `RetestRequirement`. Canonical runtime/evidence owners still decide whether supplied evidence is valid/trusted and whether any gate is satisfied.

## 7. Determinism

Proposal IDs are stable hashes derived from:

```text
source issue id
critic
category
proposal object type
```

The same unresolved issue therefore produces the same proposal IDs across repeated advisory planning calls.

Deterministic identity improves traceability and prevents duplicate repair chains from being created accidentally.

## 8. Safety / authority guards

Tests statically reject imports/calls to:

```text
ProviderManagedRunner
ManagedFlowController
ProductionReleaseController
gate_evidence_errors
run_target_command
release_action
merge_pull_request
```

They also reject code paths that directly set:

```text
RepairDirectiveStatus.ACCEPTED
RetestStatus.PASSED
```

## 9. Acceptance criteria

A45.1 is complete when:

- [x] unresolved critique issues produce A41 repair proposal objects;
- [x] all generated root causes remain PROPOSED;
- [x] all generated repair directives remain PROPOSED;
- [x] all generated retests remain PENDING with no fabricated evidence;
- [x] P0 repair proposals require human approval;
- [x] repeated issue IDs deduplicate in batch proposal mode;
- [x] RESOLVED issues cannot receive a new direct proposal;
- [x] proposal IDs are deterministic;
- [x] no execution/gate/release owner is imported;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 10. Handoff

After A45.1 is green and merged, the next step should be A45.2: a **repair lineage graph adapter** that projects proposal bundles into the existing `EvidenceGraph` relationship vocabulary (`CAUSED_BY`, `REPAIRED_BY`, `REQUIRES_RETEST`) without mutating canonical evidence or claiming that a repair/retest happened.
