# A50.9B — EV Controlled Index Trial

Status: **VERIFIED / CANARY_PASS**  
Date: **2026-10-02**

## Trigger

A50.8 completed blind human review and derived:

```text
EV / OCPP → ACCEPT_FOR_INDEX_TRIAL
```

That verdict does not authorize canonical promotion. A50.9B therefore tests the accepted EV draft in a temporary canary index without editing `skills_UIUX/knowledge/index.json`.

## Canary topology

```text
canonical index: 3 records
+ EV/OCPP draft: 1 record
= temporary canary index: 4 records
```

The canary manifest exists only inside a temporary workspace created by the evaluator.

The accepted draft is:

```text
knowledge.domain.ev-charging-ocpp-transaction-semantics.v1
```

## Preconditions

A50.9B fails closed unless:

- merged A50.8 EV verdict is `ACCEPT_FOR_INDEX_TRIAL`;
- A50.8 independent human review is complete;
- no material regression was reported;
- joint specificity/actionability + decision-usefulness win is true;
- correctness and unsupported-claim-risk guards are clear;
- A50.7 still reports the EV candidate as `KEEP_DRAFT`;
- GenAI/NIST remains `HOLD_FRESHNESS_REVIEW`;
- canonical Knowledge OS index remains exactly three records.

## Retrieval checks

### EV isolation

The real `KnowledgeRetriever` runs against the four-record canary index for a mobility/EV design query. Verified result:

```text
hits = [EV/OCPP record]
other 3 records = domain_mismatch
vector_search_used = false
```

### Canonical regression

The same canonical queries used for Nova/Lumen/CENNEXT are run against both:

```text
canonical 3-record index
canary 4-record index
```

The hit IDs remain identical. The EV record is excluded by `domain_mismatch` for every canonical-domain query.

### Negative cross-domain isolation

The canary is also queried with:

```text
education-edtech
ai-software
```

Neither domain retrieves the EV record or any unrelated canonical record.

## Usefulness evidence

A50.9B does not invent a new human review. It reuses only the already-recorded A50.8 human result as an acceptance precondition:

```text
EV knowledge preferred
material regression = false
specificity/actionability > baseline
decision usefulness > baseline
correctness >= baseline
unsupported-claim risk >= baseline
```

That evidence remains advisory and is not runtime/product evidence.

## Rollback verification

The evaluator records the canonical `index.json` bytes/hash before canary execution.

Inside the temporary workspace it builds:

```text
canary-index.json   = canonical refs + EV draft ref
rollback-index.json = original canonical refs only
```

Verified rollback result:

- rollback index loads exactly the original canonical record IDs;
- canonical `index.json` bytes remain unchanged after the trial;
- canonical hash before equals canonical hash after;
- the temporary workspace is discarded.

## Decision

Allowed trial decisions:

```text
CANARY_PASS
CANARY_FAIL
```

Final verified result:

```text
CANARY_PASS
usefulness_evidence_clear = true
ev_retrieval_isolated = true
canonical_retrieval_regression_clear = true
negative_domain_isolation_clear = true
context_budget_clear = true
rollback_verified = true
genai_hold_preserved = true
promotion_proposal_allowed = true
```

## Authority boundary

Even `CANARY_PASS` only sets:

```text
promotion_proposal_allowed = true
```

It never sets:

```text
index_mutation_allowed = true
canonical_promotion_allowed = true
auto_promotion_allowed = true
vector_search_change_allowed = true
product_evidence = true
```

A separate explicit promotion proposal/governance task is required before any canonical index mutation.

## Verification

Functional head `10c171f97ce65e4c5e69a090acafa2467435e0e1` passed:

- UIUX Factory CI #1479 — SUCCESS
  - A50.9B validator — `CANARY_PASS`
  - 639 foundation tests passed
- A20 UIUX Factory v1 Release Candidate #138 — SUCCESS
  - full Factory regression — SUCCESS
  - structural/security audit — SUCCESS
  - pinned Nova/Lumen/CENNEXT dogfood — SUCCESS

A first CI attempt correctly caught an evaluator implementation bug: `KnowledgeIndex.load()` returns internal indexed-record wrappers rather than raw `KnowledgeRecord` objects. The evaluator was fixed to read `item.record.id` and canonical exclusion `record_ref`; no canary threshold or regression case was weakened.

## GenAI boundary

GenAI/NIST is not part of this canary and remains:

```text
HOLD_FRESHNESS_REVIEW
```

## Next step

A50.9B permits only a separate canonical-promotion proposal. The canonical corpus remains three records until an explicit later governance task authorizes and verifies an index mutation.
