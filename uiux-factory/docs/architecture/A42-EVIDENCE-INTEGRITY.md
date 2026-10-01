# A42.2 — Evidence Integrity

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A42.1 Evidence Graph Foundation + A41 critique/repair contracts + A40 architecture guardrails

## 1. Purpose

A42.2 hardens the Brain evidence relationship layer against false-evidence promotion and broken lineage.

It validates that:

- graph evidence nodes are exact adapter projections of canonical runtime/provenance/release evidence;
- reasoning/control nodes cannot invent trusted-evidence flags;
- provider/model claims cannot masquerade as trusted runtime verification;
- critique/repair/retest references resolve to canonical evidence IDs;
- repair lineage is structurally complete;
- at least one typed end-to-end chain can be traced from task framing to canonical evidence when the graph claims complete lineage.

A42.2 remains advisory integrity validation. It does **not** own runtime gates, release readiness, evidence trust or repair execution.

Canonical implementation:

```text
core/brain_os/adapters/evidence.py
core/brain_os/reasoning/evidence_integrity.py
core/brain_os/reasoning/lineage_integrity.py
```

Executable tests:

```text
tests/test_brain_evidence_integrity_a42.py
tests/test_brain_end_to_end_lineage_a42.py
tests/test_brain_evidence_graph_a42.py
tests/test_architecture_guardrails_a40.py
```

## 2. Canonical evidence comparison index

A42.2 extends the A42.1 evidence adapter with:

```text
canonical_evidence_index(...)
```

The index is built only from existing canonical objects:

```text
runtime EvidenceRecord
EvidenceProvenanceRecord (EVID-*)
ReleaseEvidenceArtifact (REL-*)
```

Each object is projected through the same A42.1 adapter used by the graph.

The index is temporary comparison data only. It is not:

- an evidence store;
- an evidence registry;
- a new trust authority;
- a release registry;
- persisted Brain truth.

Duplicate projected canonical IDs are rejected.

## 3. False-evidence protections

`validate_evidence_integrity(...)` checks graph evidence nodes against the canonical adapter projection.

It detects:

```text
CANONICAL_REF_MISSING
CANONICAL_EVIDENCE_MISSING
CANONICAL_PROJECTION_MISMATCH
DUPLICATE_CANONICAL_REF
BRAIN_TRUST_CLAIM
NON_RUNTIME_TRUST_OVERRIDE
VERIFIED_BY_NON_EVIDENCE
UNTRUSTED_RUNTIME_VERIFICATION
```

Important rules:

- a reasoning node such as Decision or CritiqueIssue cannot assign itself `canonical_trusted_flag=true`;
- provenance/release graph nodes do not receive a Brain-computed trusted flag;
- runtime graph metadata must match the adapter projection of the canonical `EvidenceRecord`;
- a `VERIFIED_BY` relation cannot terminate in model/provider prose represented as untrusted runtime evidence;
- the validator never upgrades an untrusted record.

## 4. Repair-lineage integrity

`validate_repair_lineage_integrity(...)` validates one `RepairLink` and its referenced objects:

```text
CritiqueIssue
→ RootCause
→ RepairDirective
→ RetestRequirement
→ canonical evidence
```

It verifies:

- every RepairLink object reference exists;
- corresponding graph nodes exist with the correct kind;
- root causes point back to issues in the same RepairLink;
- repair directives point to issues/root causes in the same RepairLink;
- retests point to a repair directive in the same RepairLink;
- required `CAUSED_BY`, `REPAIRED_BY`, `REQUIRES_RETEST` and `VERIFIED_BY` edges exist;
- terminal retest evidence refs resolve to canonical evidence graph nodes;
- terminal retests cannot rely on untrusted runtime evidence;
- resolved critique evidence/retest refs resolve inside the same lineage bundle.

A `PENDING` or `BLOCKED` retest may be structurally valid while `lineage_complete=false`.

This distinction matters:

```text
integrity_valid = graph/refs are internally truthful
lineage_complete = the trace has reached terminal evidence
```

Neither field means a product/runtime/release gate passed.

## 5. Full task-to-evidence lineage

`validate_end_to_end_lineage(...)` checks for at least one typed path:

```text
TASK
  JUSTIFIES
HYPOTHESIS
  SUPPORTS | CONTRADICTS
DECISION
  REFERENCES
CRITIQUE_ISSUE
  CAUSED_BY
ROOT_CAUSE
  REPAIRED_BY
REPAIR_DIRECTIVE
  REQUIRES_RETEST
RETEST_REQUIREMENT
  VERIFIED_BY
canonical evidence
```

If an upstream edge is missing, the report remains advisory but marks `lineage_complete=false`.

If the terminal runtime evidence is untrusted, integrity is invalid.

The validator does not infer missing edges and does not convert partial lineage into a complete one.

## 6. Integrity report semantics

A42.2 introduces strict immutable report types:

```text
EvidenceIntegrityFinding
EvidenceIntegrityReport
IntegrityCode
IntegritySeverity
```

`EvidenceIntegrityReport` exposes:

```text
integrity_valid
lineage_complete
findings
```

This is intentionally **not** named `PASS`, `gate_status`, `release_ready` or similar.

The report answers only:

> Is the Brain relationship representation internally consistent with canonical evidence and declared lineage?

It does not answer:

> Did QA pass? Is the design good? Did the repair execute? Is the product ready to release?

Those remain owned by the existing runtime/QA/release systems and human authority.

## 7. Existing authority remains unchanged

A42.2 does not modify:

```text
core/runtime/flow_os/evidence.py
core/provenance/evidence_lineage.py
core/provenance/release_evidence_registry.py
```

It does not redefine:

```text
EvidenceRecord
TRUSTED_EVIDENCE_TYPES
gate_evidence_errors
release_ready
```

It introduces no Brain-owned evidence store, policy file, gate evaluator or release controller.

## 8. Acceptance criteria

A42.2 is complete when:

- [x] canonical evidence projections can be compared without creating a second evidence store;
- [x] tampered runtime evidence metadata/trust is detected;
- [x] Brain-authored trusted flags are rejected as integrity errors;
- [x] provider claims cannot terminate a trusted verification chain;
- [x] critique/repair/retest evidence refs must resolve to canonical evidence graph nodes;
- [x] required repair-lineage nodes and edges are validated;
- [x] pending/blocked retests remain incomplete rather than falsely terminal;
- [x] full task → hypothesis → decision → critique → cause → repair → retest → evidence path can be validated;
- [x] missing upstream lineage is reported as incomplete rather than inferred;
- [x] no runtime/provenance/release authority is moved into Brain OS;
- [ ] final PR head passes UIUX Factory CI;
- [ ] final PR head passes A20 release-candidate regression/dogfood.

## 9. Handoff

After A42.2 is green, the next roadmap package is A43.1 — Flow Selection Engine.

A43 must use the canonical Flow OS and A40 ownership rules. Evidence Integrity remains an advisory reasoning/control check and must not become a prerequisite gate engine hidden inside Brain routing.
