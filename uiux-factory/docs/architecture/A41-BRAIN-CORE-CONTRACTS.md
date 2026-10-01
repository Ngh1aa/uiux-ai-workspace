# A41.1 — Brain Core Contracts

Status: **IMPLEMENTED / VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A40.1 Architecture Reconciliation + A40.2 Architecture Guardrails

## 1. Purpose

A41.1 introduces the first concrete Brain OS package as strict data/control contracts only.

It does **not** add a Brain runtime, provider, tool loop, flow planner, gate engine, evidence authority, merge authority or release authority.

Canonical implementation:

```text
uiux-factory/core/brain_os/contracts.py
```

Executable tests:

```text
uiux-factory/tests/test_brain_core_contracts_a41.py
uiux-factory/tests/test_architecture_guardrails_a40.py
```

## 2. Contracts introduced

### BrainTaskFrame

A reasoning frame derived from the canonical Task Contract. It carries:

- goal;
- intent;
- domain;
- product archetype;
- change surface;
- validation lane;
- inherited authority context;
- risk;
- constraints / preserve / forbidden rules;
- success criteria;
- evidence references;
- uncertainty records;
- source Task Contract version/confidence/inference evidence.

`BrainTaskFrame.authority` is descriptive context only. It does not grant or elevate execution authority.

### Uncertainty

Canonical states:

```text
KNOWN
INFERRED
PROPOSED
VALIDATED
BLOCKED
CONFLICTED
```

Rules:

- `VALIDATED` requires linked evidence;
- `BLOCKED` requires at least one explicit blocker;
- confidence is bounded to `0.0..1.0`.

### Hypothesis

Carries:

```text
statement
risk
confidence
validation_method
status
assumptions
evidence_refs
blockers
```

A hypothesis cannot be marked `VALIDATED` or `REJECTED` without evidence references. A `BLOCKED` hypothesis must state its blocker.

### Decision

Carries:

```text
question
chosen option
alternatives
evidence_refs
tradeoff
reversibility
confidence
status
owner
selection provenance
blockers
supersession link
```

`SELECTED` requires `selected_by` provenance. This records who/what selected a path; it does not bypass runtime/human authority boundaries.

## 3. Strictness rules

All A41.1 Brain contracts are:

```text
extra = forbid
frozen = true
```

This prevents arbitrary fields from silently becoming policy or execution controls and makes persisted/serialized reasoning state deterministic enough for later ledger/memory work.

## 4. Relationship to existing runtime

A41.1 deliberately does not redefine:

```text
TaskContract
GoalInterpreter
FlowPlanner
EvidenceRecord
TRUSTED_EVIDENCE_TYPES
ManagedFlowController
ProviderManagedRunner
ProductionReleaseController
```

The canonical owners from A40 remain unchanged.

A43 will later introduce the adapter that constructs/updates Brain framing around canonical GoalInterpreter/FlowPlanner output. A41.1 only establishes the target schemas.

## 5. Evidence semantics

Brain contract `evidence_refs` fields contain references only. They do not turn referenced claims into trusted runtime evidence.

Trust remains owned by existing evidence/provenance layers. Later A42 may relate hypothesis/decision IDs to current evidence IDs through adapters, but it must preserve existing trusted/untrusted semantics.

## 6. Acceptance criteria

A41.1 is complete when:

- [x] `BrainTaskFrame` exists as a strict immutable contract;
- [x] `Uncertainty` implements KNOWN / INFERRED / PROPOSED / VALIDATED / BLOCKED / CONFLICTED;
- [x] validated uncertainty requires evidence;
- [x] `Hypothesis` records risk/confidence/validation method/status/evidence;
- [x] validated/rejected hypothesis requires evidence;
- [x] `Decision` records alternatives, evidence, tradeoff and reversibility;
- [x] selected decisions require provenance;
- [x] contracts reject extra fields and invalid authority/change-surface values;
- [x] Brain contracts serialize and round-trip;
- [x] canonical A40 architecture guardrails remain applicable;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression.

## 7. Handoff

After A41.1 is green, A41.2 should add the critique/repair contracts needed to connect future critics to bounded replanning:

```text
CritiqueIssue
RootCause
RepairDirective
RepairLink
RetestRequirement
```

A41.2 must remain contract-only; orchestration belongs to A44/A45.
