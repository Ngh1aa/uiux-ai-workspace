# A42.1 — Evidence Graph Foundation

Status: **IMPLEMENTED / VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A40 Architecture Guardrails + A41 Brain Core / Critique & Repair Contracts

## 1. Purpose

A42.1 introduces a Brain OS **relationship graph over canonical evidence references**.

It does not create a new evidence authority, evidence store, gate evaluator, release registry or persistence subsystem.

The graph exists so Brain reasoning objects can be connected to evidence that is already owned by the runtime/provenance/release layers.

Canonical implementation:

```text
uiux-factory/core/brain_os/reasoning/evidence_graph.py
uiux-factory/core/brain_os/adapters/evidence.py
```

Executable tests:

```text
uiux-factory/tests/test_brain_evidence_graph_a42.py
uiux-factory/tests/test_architecture_guardrails_a40.py
```

## 2. Existing evidence owners preserved

A42.1 adapts these existing owners rather than duplicating them:

```text
core/runtime/flow_os/evidence.py
core/provenance/evidence_lineage.py
core/provenance/release_evidence_registry.py
core/contracts/evidence_provenance_schema.py
core/contracts/release_evidence_schema.py
```

Authority remains where it already exists:

- runtime `EvidenceRecord` owns runtime trusted/untrusted semantics;
- provenance owns stable `EVID-*` reference evidence identity;
- release registry owns `REL-*` release artifact identity and release claim aggregation;
- runtime/QA/release gates continue deciding whether evidence satisfies a gate.

The Brain graph cannot upgrade any reference into trusted evidence.

## 3. Evidence adapters

`core/brain_os/adapters/evidence.py` provides projections for:

### Runtime evidence

```text
EvidenceRecord
→ EvidenceGraphNode(kind=RUNTIME_EVIDENCE)
```

The adapter preserves:

- canonical evidence ID;
- status;
- origin;
- runtime trusted flag;
- evidence type/stage/tool tags.

The copied `canonical_trusted_flag` is informational only. Brain OS does not recompute or enforce it.

### Provenance evidence

```text
EvidenceProvenanceRecord (EVID-*)
→ EvidenceGraphNode(kind=PROVENANCE_EVIDENCE)
```

The stable `EVID-*` identity remains canonical.

### Release evidence

```text
ReleaseEvidenceArtifact (REL-*)
→ EvidenceGraphNode(kind=RELEASE_EVIDENCE)
```

The graph references registry artifacts but does not recalculate `release_ready` or deployment truth.

## 4. Relationship graph

The graph adds only relationship-level primitives:

```text
EvidenceGraphNode
EvidenceGraphEdge
EvidenceGraph
```

Brain node kinds include:

```text
TASK
HYPOTHESIS
DECISION
CRITIQUE_ISSUE
ROOT_CAUSE
REPAIR_DIRECTIVE
RETEST_REQUIREMENT
```

Canonical evidence anchors include:

```text
RUNTIME_EVIDENCE
PROVENANCE_EVIDENCE
RELEASE_EVIDENCE
ARTIFACT
```

Relationships include bounded semantic edges such as:

```text
SUPPORTS
CONTRADICTS
JUSTIFIES
CAUSED_BY
REPAIRED_BY
REQUIRES_RETEST
RETESTED_BY
VERIFIED_BY
REFERENCES
SUPERSEDES
PRODUCED
```

## 5. Intended lineage

A42.1 makes this lineage representable without changing execution behavior:

```text
Task
→ Hypothesis
→ Decision
→ CritiqueIssue
→ RootCause
→ RepairDirective
→ RetestRequirement
→ canonical runtime/provenance/release evidence
```

This is a traceability graph, not a workflow engine.

## 6. Integrity rules

The graph is strict and immutable through the existing Brain contract base.

It enforces:

- unique node IDs;
- unique edge IDs;
- no dangling edge endpoints;
- no self edges;
- bounded node/relation vocabulary;
- canonical refs remain explicit rather than copied into a new evidence record format.

The graph does **not** expose methods to:

- mark a gate passed;
- change runtime trusted evidence;
- execute a repair;
- deploy/merge/release;
- persist evidence independently;
- overwrite provenance or registry state.

## 7. No second evidence store

A42.1 intentionally does not create:

```text
brain_os/evidence_store.py
brain_os/evidence_registry.py
brain_os/runtime-policy.json
brain_os/provider-policy.json
brain_os/release-policy.json
```

Later persistence/ledger work must preserve canonical IDs and authority boundaries instead of copying evidence into a parallel truth source.

## 8. Acceptance criteria

A42.1 is complete when:

- [x] Brain can represent task/hypothesis/decision/critique/repair/retest relationships;
- [x] runtime `EvidenceRecord` can be referenced without changing its trusted flag;
- [x] provider claims remain untrusted when projected into the graph;
- [x] stable provenance `EVID-*` IDs are preserved;
- [x] release artifact `REL-*` IDs are preserved;
- [x] graph rejects duplicate nodes/edges, dangling endpoints and self edges;
- [x] graph round-trips through strict serialization;
- [x] A40 evidence adapter guardrails remain satisfied;
- [x] no Brain-owned evidence store/policy surface is introduced;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression.

## 9. Handoff

After A42.1 is green, A42.2 should implement **Evidence Integrity** around graph linkage and provenance validation, including false-evidence protection and end-to-end lineage checks.

A42.2 must continue to use existing runtime/provenance evidence as truth rather than assigning trust from Brain graph relationships.
