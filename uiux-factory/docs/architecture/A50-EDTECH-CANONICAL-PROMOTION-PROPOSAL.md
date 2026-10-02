# A50.11 — EdTech/LTI Canonical Promotion Proposal / Governance

Status: **OWNER-DELEGATED APPROVAL FOR SEPARATE IMPLEMENTATION TASK / NO PROMOTION IN THIS PHASE**  
Date: **2026-10-02**

## Purpose

Convert the merged A50.9C EdTech/LTI v2 `CANARY_PASS` into a bounded canonical-promotion proposal on top of the post-EV four-record Knowledge OS baseline.

This phase does not create canonical EdTech assets and does not edit `skills_UIUX/knowledge/index.json`.

## Evidence lineage

Historical A50.9C evidence is bound to merged PR #119:

```text
head = d25af8fe25b69a7fe3460acff323ffe6083d5aa9
merge = 335e2aefd03a5404493391823c33d10a1626e747
decision = CANARY_PASS
prior verdict = ACCEPT_FOR_INDEX_TRIAL
promotion_proposal_allowed = true
```

The historical canary verified EdTech retrieval isolation, Nova/Lumen/CENNEXT regression safety, EV/AI negative isolation, context budget, rollback and GenAI HOLD. Those three-record canary executables remain historical evidence and are not re-run against the current four-record topology.

## Current baseline

A50.11 requires `knowledge-canonical-state-v2` and the exact EV-inclusive four-record canonical index:

```text
financial-services
art-culture
industrial-services
mobility-ev
```

The EdTech v2 revision must remain unindexed and its proposed canonical record/content files must not exist during this proposal phase.

## Source freshness

Freshness was rechecked on 2026-10-02 against official 1EdTech surfaces. Current source truth remains:

```text
LTI core = LTI 1.3
LTI Advantage = AGS 2.0 + NRPS 2.0 + Deep Linking 2.0
```

This matches the EdTech v2 candidate's source scope and metadata. A future implementation task must still recheck source freshness immediately before canonical mutation.

## Governance

The repository owner `Haign12` explicitly authorized bounded continuation and equivalent intermediate approvals after mandatory gates pass. A50.11 records that as `owner_delegated_governance`; it does not fabricate an independent-human review.

The derived verdict is allowed to become:

```text
APPROVED_FOR_EXPLICIT_PROMOTION_TASK
```

only when historical evidence, current four-record baseline, source freshness, authority boundary, retrieval regression, negative isolation, rollback contract, GenAI HOLD and owner-delegation boundaries all pass.

Even then:

```text
index_mutation_allowed = false
canonical_promotion_in_this_proposal = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

## Required future implementation controls

A separate EdTech promotion implementation task must:

1. recheck official 1EdTech freshness;
2. preserve the existing four canonical records including EV;
3. copy revision content into the canonical namespace;
4. copy the record and rewrite `content_ref` to the canonical content path;
5. validate `KnowledgeRecord` before index mutation;
6. add exactly one EdTech canonical index ref (4 → 5);
7. rerun retrieval for financial/art/industrial/EV/EdTech;
8. rerun AI negative isolation;
9. verify context budgets and vector-search-disabled state;
10. verify rollback restores the exact four-record pre-EdTech index and removes only the new EdTech canonical files;
11. preserve GenAI/NIST `HOLD_FRESHNESS_REVIEW`;
12. never infer product evidence from canonical knowledge acceptance.

Final retrospective owner review remains deferred until the broader `uiux-ai-workspace` upgrade is complete.
