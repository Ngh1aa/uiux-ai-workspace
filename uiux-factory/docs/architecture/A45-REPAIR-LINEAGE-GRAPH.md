# A45.2 — Repair Lineage Graph Adapter

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A42 Evidence Graph + A45.1 Repair Proposal Orchestrator

## 1. Purpose

A45.2 projects A45.1 proposal-only repair bundles into the existing A42 `EvidenceGraph` relationship vocabulary.

Canonical implementation:

```text
core/brain_os/adapters/repair_lineage.py
```

The adapter does not create a second graph model or evidence store.

## 2. Projected proposal lineage

For one unresolved critique issue and one matching `RepairProposalBundle`, the adapter creates:

```text
CritiqueIssue
  CAUSED_BY
RootCause(PROPOSED)
  REPAIRED_BY
RepairDirective(PROPOSED)
  REQUIRES_RETEST
RetestRequirement(PENDING)
```

The fragment deliberately stops at the pending retest.

It does **not** create:

```text
RETESTED_BY
VERIFIED_BY
runtime evidence nodes
provenance evidence nodes
release evidence nodes
```

because proposal creation is not repair execution or verification.

## 3. RepairLineageFragment

Each projection returns:

```text
source_issue_id
4 relationship nodes
3 relationship edges
advisory_only = true
execution_claim = false
verification_claim = false
evidence_effect = none
gate_effect = none
```

The fragment validator permits only this exact proposal shape.

## 4. Source identity

Node identity follows the existing A42 naming convention:

```text
critique:<CritiqueIssue.id>
root:<RootCause.id>
repair:<RepairDirective.id>
retest:<RetestRequirement.id>
```

Proposal nodes preserve their A41 IDs through `canonical_ref` for relationship identity only. They do not gain canonical evidence trust.

Every proposal node has:

```text
canonical_trusted_flag = null
```

## 5. Graph extension

`extend_graph_with_repair_proposal(...)` returns a **new** immutable `EvidenceGraph`.

It:

- preserves the input graph unchanged;
- reuses an identical existing critique/proposal node when present;
- is idempotent when the same proposal is applied repeatedly;
- rejects a node/edge ID collision when existing content differs;
- preserves graph id, task ref, schema version and warnings.

## 6. Truth boundary

A projected repair proposal does not complete end-to-end lineage.

After projection, A42 `validate_end_to_end_lineage(...)` should still report the path incomplete at the retest → canonical evidence step until real trusted evidence is attached through the canonical evidence adapters and a truthful `VERIFIED_BY` relationship exists.

This is intentional.

## 7. Input validation

Projection rejects proposal bundles when:

- `source_issue_id` differs from the supplied critique issue;
- root cause does not reference exactly the source issue;
- directive does not reference exactly the source issue/root cause;
- retest does not reference the proposed directive.

This prevents mismatched repair chains from entering the graph.

## 8. Authority boundary

The adapter does not import/call:

```text
EvidenceRecord
effective_evidence
gate_evidence_errors
ProviderManagedRunner
ManagedFlowController
run_target_command
release_action
ProductionReleaseController
merge_pull_request
```

It cannot:

- execute the proposed repair;
- run the proposed retest;
- create canonical evidence;
- upgrade trust;
- satisfy a runtime gate;
- mark an issue resolved;
- merge/deploy/release.

## 9. Acceptance criteria

A45.2 is complete when:

- [x] A45.1 proposal bundles project into existing A42 node/edge types;
- [x] the fragment contains only CAUSED_BY / REPAIRED_BY / REQUIRES_RETEST;
- [x] no VERIFIED_BY or RETESTED_BY edge is fabricated;
- [x] no proposal node carries a trusted-evidence flag;
- [x] graph extension is immutable and idempotent;
- [x] conflicting graph identity is rejected;
- [x] mismatched source issue/proposal lineage is rejected;
- [x] A42 end-to-end lineage remains incomplete until canonical retest evidence exists;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 10. Handoff

After A45.2 is green and merged, the next step should be **A45.3 — repair proposal benchmark / policy guard**: a deterministic corpus covering critic → target stage → required retest evidence mapping and graph shape, with explicit regression protection against accidental auto-execution or false verification semantics.
