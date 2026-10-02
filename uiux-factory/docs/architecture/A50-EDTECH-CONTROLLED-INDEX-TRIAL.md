# A50.9C — EdTech Controlled Index Trial

Status: **CONTROLLED CANARY / NO CANONICAL PROMOTION**  
Date: **2026-10-02**

## Purpose

Run the EdTech/LTI v2 record through the same bounded canary discipline proven by A50.9B for EV/OCPP, after the completed A50.9A human review derived `ACCEPT_FOR_INDEX_TRIAL`.

This task is an index trial only. It does not authorize canonical promotion.

## Preconditions

The evaluator requires the merged A50.9A result to remain:

```text
verdict = ACCEPT_FOR_INDEX_TRIAL
human_review_complete = true
material_regression = false
joint_usefulness_win = true
correctness_guard_clear = true
unsupported_claim_risk_guard_clear = true
required_state_guidance_present = true
shadow_retrieval_isolated = true
```

The accepted candidate is exactly:

```text
knowledge.domain.edtech-lti-context-roles-services.v2
skills_UIUX/knowledge/revisions/records/edtech-lti-context-roles-services-v2.json
domain = education-edtech
stage = design
```

The v1 EdTech draft/history remains unchanged.

## Canary topology

```text
canonical index: 3 records
+
EdTech/LTI v2 revision: 1 record
=
temporary canary index: 4 records
```

The canonical `skills_UIUX/knowledge/index.json` is read before and after the trial and must remain byte-identical with the same SHA-256 hash.

## Required checks

A `CANARY_PASS` requires all of the following:

1. EdTech v2 is still unindexed before the canary.
2. The real `KnowledgeIndex` + `KnowledgeRetriever` returns only EdTech v2 for the EdTech query.
3. Nova, Lumen and CENNEXT canonical retrieval results are identical before vs canary.
4. Mobility/EV and AI-software negative-domain queries receive no EdTech hit.
5. Vector retrieval remains disabled.
6. Delivered EdTech context stays within the declared context budget.
7. Rollback restores the exact canonical record set.
8. Canonical `index.json` bytes/hash remain unchanged.
9. GenAI/NIST remains `HOLD_FRESHNESS_REVIEW`.
10. A50.9A human usefulness/safety evidence remains clear.

Any failed check yields `CANARY_FAIL`.

## Decision boundary

Even `CANARY_PASS` means only:

```text
promotion_proposal_allowed = true
```

It never means:

```text
index_mutation_allowed = false
canonical_promotion_allowed = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

A separate explicit canonical-promotion proposal and governance review is required before EdTech could ever be added to the canonical index.

## Regression surface

- benchmark contract: `benchmarks/knowledge-edtech-controlled-index-trial-v1.json`
- evaluator: `core/benchmarks/knowledge_edtech_controlled_index_trial.py`
- validator: `scripts/validate_knowledge_edtech_controlled_index_trial.py`
- tests: `tests/test_knowledge_edtech_controlled_index_trial_a50.py`

The CI validator is intentionally fail-closed and expects `CANARY_PASS` while preserving every no-promotion boundary above.
