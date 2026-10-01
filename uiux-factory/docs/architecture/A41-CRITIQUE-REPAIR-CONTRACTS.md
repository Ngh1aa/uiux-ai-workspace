# A41.2 — Critique & Repair Contracts

Status: **VERIFIED / MERGED TO MAIN**  
Date: **2026-10-02**  
Merged via: PR #80 → `main@fc2f620fbd1ff4e197bbbfe022d5883b15481178`  
Depends on: A41.1 Brain Core Contracts + A40 Architecture Guardrails

## 1. Purpose

A41.2 adds strict immutable Brain OS contracts for converting critique findings into traceable repair/retest lineage.

It does **not** add critic orchestration, automatic root-cause selection, execution tools, repair execution, replanning behavior, gate authority, provider authority or release authority.

Canonical implementation:

```text
uiux-factory/core/brain_os/critique_contracts.py
```

Executable tests:

```text
uiux-factory/tests/test_brain_critique_repair_contracts_a41.py
uiux-factory/tests/test_architecture_guardrails_a40.py
```

## 2. Contract lineage

```text
CritiqueIssue
    ↓
RootCause
    ↓
RepairDirective
    ↓
RetestRequirement
    ↓
RepairLink
```

`RepairLink` records references between the objects; it is not an execution engine.

## 3. Contracts introduced

### CritiqueIssue

Captures one critic finding:

```text
critic
category
severity
status
summary
rationale
evidence_refs
affected_artifacts
blockers
retest_refs
```

Rules:

- `CONFIRMED` requires evidence references;
- `BLOCKED` requires blockers;
- `RESOLVED` requires both evidence and at least one retest reference;
- model prose alone cannot close an issue.

### RootCause

Captures a bounded causal explanation tied to one or more critique issues.

Rules:

- at least one issue reference is mandatory;
- `SUPPORTED` and `REJECTED` require evidence;
- `BLOCKED` requires blockers;
- confidence is bounded to `0.0..1.0`.

### RepairDirective

Captures a proposed/accepted repair instruction:

```text
issue_ids
root_cause_ids
target_stage
instruction
rationale
expected_outcome
priority
status
constraints
evidence_refs
blockers
accepted_by
defer_reason
requires_human_approval
```

Important boundary: there is deliberately **no `APPLIED`/`EXECUTED` status** in this contract. A Brain directive is not proof that target-project work occurred.

Rules:

- issue and root-cause lineage are mandatory;
- `ACCEPTED` requires acceptance provenance;
- `DEFERRED` requires a reason;
- `BLOCKED` requires blockers.

### RetestRequirement

Defines what must be proven after a repair:

```text
repair_directive_id
stage
evidence_types
acceptance_criteria
status
evidence_refs
blockers
```

Rules:

- at least one evidence type and acceptance criterion are required;
- `PASSED` and `FAILED` require evidence references;
- `BLOCKED` requires blockers;
- no retest status changes runtime gate truth by itself.

### RepairLink

Provides a traceable lineage bundle across:

```text
issue_ids
root_cause_ids
repair_directive_ids
retest_requirement_ids
```

All four reference groups are required and deduplicated.

## 4. Strictness / authority boundaries

A41.2 models inherit the A41.1 Brain contract base:

```text
extra = forbid
frozen = true
```

They contain reasoning/control metadata only.

They do not:

- import provider execution surfaces;
- write target files;
- run validators/browser tools;
- satisfy runtime gates;
- grant merge/release authority;
- redefine `EvidenceRecord` or trusted-evidence types;
- create a parallel repair runtime.

Existing A40 architecture guardrails continue to enforce those boundaries.

## 5. Evidence semantics

All `evidence_refs` are references only. The referenced evidence remains authoritative only if the existing runtime/provenance layers consider it trusted.

This prevents future critics from converting their own prose into evidence merely by putting a string into `evidence_refs`.

A42 defines adapter-backed relationships between Brain objects and existing evidence/provenance IDs.

## 6. Acceptance criteria

A41.2 is complete:

- [x] `CritiqueIssue` exists with severity/status/evidence semantics;
- [x] confirmed/resolved issues require evidence;
- [x] resolved issues require retest lineage;
- [x] `RootCause` requires critique lineage and evidence for supported/rejected states;
- [x] `RepairDirective` requires issue/root-cause lineage;
- [x] accepted/deferred/blocked repair states require provenance/reason/blockers;
- [x] repair directives cannot claim an `APPLIED` execution state;
- [x] `RetestRequirement` requires evidence type + acceptance criteria;
- [x] terminal retest states require evidence;
- [x] `RepairLink` requires complete issue → cause → directive → retest lineage;
- [x] contracts serialize, round-trip, reject extras and remain immutable;
- [x] UIUX Factory CI #1075 — SUCCESS;
- [x] A20 release-candidate #37 — SUCCESS;
- [x] full regression + Nova/Lumen/CENNEXT dogfood — SUCCESS.

## 7. Handoff

A42 begins **Evidence Graph Foundation** as an adapter/relationship layer over existing evidence and provenance primitives.

A42 must not build a second independent evidence authority/store.
