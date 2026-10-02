# A50.10A — EV Canonical Promotion Proposal / Governance Review

Status: **PROPOSAL READY / HUMAN GOVERNANCE PENDING / NO PROMOTION**  
Date: **2026-10-02**

## Purpose

Convert the verified A50.9B EV/OCPP `CANARY_PASS` into a bounded canonical-promotion proposal and explicit governance review surface.

This phase deliberately does **not** promote the candidate. It establishes the controls and decision record required before a separate canonical-promotion implementation task can exist.

## Earned preconditions

The executable proposal evaluator re-runs A50.9B and requires:

```text
canary decision = CANARY_PASS
promotion_proposal_allowed = true
rollback_verified = true
canonical_retrieval_regression_clear = true
negative_domain_isolation_clear = true
genai_hold_preserved = true
canonical index = 3
EV candidate remains unindexed
```

The candidate is:

```text
knowledge.domain.ev-charging-ocpp-transaction-semantics.v1
source namespace = skills_UIUX/knowledge/drafts/
proposed future canonical namespace = skills_UIUX/knowledge/{records,content}/
```

## Governance decision

Allowed review verdicts are exactly:

```text
APPROVE_PROMOTION_TASK
REVISE_PROPOSAL
HOLD
REJECT
```

The checked-in review ledger starts fail-closed:

```text
review_status = PENDING
decision = GOVERNANCE_REVIEW_REQUIRED
separate_promotion_task_allowed = false
```

`APPROVE_PROMOTION_TASK` requires an independent human reviewer to explicitly confirm:

```text
source_freshness_rechecked = true
rollback_plan_accepted = true
cross_domain_risk_accepted = true
```

Even that approval only permits a **separate explicit promotion implementation task**. It does not mutate the index in this phase.

## Non-negotiable boundary

For this proposal/review phase:

```text
index_mutation_allowed = false
canonical_promotion_in_this_proposal = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

The evaluator also fails if the proposed canonical EV record/content files already exist or if the EV record appears in the canonical index during proposal review.

## Future promotion task controls

If governance later returns `APPROVE_PROMOTION_TASK`, a separate implementation task must still:

1. recheck current OCPP source/version freshness;
2. copy content into the canonical namespace;
3. rewrite `content_ref` to the canonical path;
4. validate the copied `KnowledgeRecord` before index mutation;
5. add exactly one canonical index ref;
6. rerun EV retrieval and Nova/Lumen/CENNEXT regression;
7. rerun EdTech/AI negative-domain isolation;
8. verify context budget and rollback;
9. keep vector search disabled;
10. preserve GenAI/NIST HOLD unless separately governed.

## Review artifacts

- proposal contract: `benchmarks/knowledge-ev-canonical-promotion-proposal-v1.json`
- human ledger: `benchmarks/knowledge-ev-canonical-promotion-review-v1.json`
- review packet: `benchmarks/knowledge-ev-canonical-promotion-review-packet-v1.md`
- evaluator: `core/benchmarks/knowledge_ev_canonical_promotion_proposal.py`
- validator: `scripts/validate_knowledge_ev_canonical_promotion_proposal.py`
- tests: `tests/test_knowledge_ev_canonical_promotion_proposal_a50.py`

No file under `skills_UIUX/knowledge/index.json`, `skills_UIUX/knowledge/records/`, or `skills_UIUX/knowledge/content/` is changed by A50.10A.
