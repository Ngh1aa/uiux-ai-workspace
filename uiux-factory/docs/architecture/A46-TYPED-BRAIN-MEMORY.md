# A46.1 — Typed Brain Memory Contracts & Store

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A41 Brain contracts + existing project-scoped EvaluationMemoryStore safety patterns

## 1. Purpose

A46.1 fills the remaining A40 memory gap for typed historical design rationale, hypothesis and decision context.

It adds:

```text
core/brain_os/memory_contracts.py
core/memory/brain_memory.py
```

This is historical advisory memory. It is not a second evidence store, task contract, flow planner or gate system.

## 2. Typed memory records

Supported record types:

```text
RationaleMemoryRecord
HypothesisMemoryRecord
DecisionMemoryRecord
```

Hypothesis and decision records embed the existing immutable A41 `Hypothesis` / `Decision` contracts rather than introducing incompatible copies.

Each record requires:

```text
project_scope
source_run_id
source_ref
created_at
```

and may preserve existing `evidence_refs` for provenance. Historical evidence references do not become current-run evidence merely because they are recalled.

Every record declares:

```text
advisory_only = true
authority_effect = none
gate_effect = none
evidence_effect = none
current_run_evidence = false
```

## 3. Stable identity

Memory IDs are deterministic hashes of:

```text
project_scope + memory kind + source_ref
```

A later snapshot of the same hypothesis/decision/rationale therefore upserts the same logical memory identity instead of silently creating duplicate histories.

## 4. Project-scoped store

`BrainMemoryStore` persists under the existing project-local memory root:

```text
<project>/.uiux-agent-runs/memory/brain-memory.json
```

It follows the safety patterns already used by `EvaluationMemoryStore`:

- resolved project scope;
- bounded record and recall limits;
- symlink/path-escape refusal;
- cross-process `RunLock`;
- atomic tempfile + `os.replace` writes;
- schema versioning;
- fail-closed parsing for unknown/malformed memory records.

A record whose `project_scope` differs from the store's resolved target project root is rejected.

## 5. Recall boundary

Recall can filter by:

```text
kind
tag
source_ref
exclude_run_id
bounded limit
```

The output is a reduced advisory projection and repeats:

```text
current_run_evidence = false
authority_effect = none
gate_effect = none
evidence_effect = none
```

`exclude_run_id` allows callers to keep historical recall separate from the current run.

Recall does not:

- select or change a flow;
- activate skills;
- alter task authority;
- satisfy a current-run gate;
- validate a hypothesis;
- select a decision;
- approve repair, merge, deployment or release.

## 6. Knowledge boundary

A46.1 does not create a universal Knowledge OS and does not copy `SKILL.md` methodology into memory.

The store is project-scoped historical reasoning context only. Reusable design/product/domain methodology remains owned by `skills_UIUX` until a separately governed Knowledge OS is explicitly introduced.

## 7. Acceptance criteria

- [x] rationale/hypothesis/decision memory types are strict and immutable;
- [x] existing A41 Hypothesis/Decision contracts are embedded rather than copied;
- [x] source run/reference provenance is mandatory;
- [x] IDs are stable per project/kind/source ref;
- [x] persistence is project-scoped, schema-versioned, bounded, locked and atomic;
- [x] cross-project writes are rejected;
- [x] malformed/unknown persisted records fail closed;
- [x] recall can exclude current-run records;
- [x] recalled memory can never be represented as current-run evidence;
- [x] memory source does not import flow/gate/execution/release owners;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 8. Handoff

After A46.1 is green and merged, A46.2 should add a **bounded memory recall adapter** into Brain reasoning context. It must attach historical memory only after canonical task/flow selection, enforce current-project/current-run boundaries, and keep memory unable to modify flow, authority, gates or evidence truth.
