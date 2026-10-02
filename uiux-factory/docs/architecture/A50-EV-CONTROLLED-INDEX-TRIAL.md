# A50.9B — EV Controlled Index Trial

Status: **IMPLEMENTED / VERIFICATION PENDING**  
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

The real `KnowledgeRetriever` runs against the four-record canary index for a mobility/EV design query. Expected result:

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

The hit IDs must remain identical. The EV record must be excluded by `domain_mismatch` for every canonical domain query.

### Negative cross-domain isolation

The canary is also queried with:

```text
education-edtech
ai-software
```

Neither domain may retrieve the EV record or any unrelated canonical record.

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

Rollback passes only if:

- rollback index loads exactly the original canonical record IDs;
- canonical `index.json` bytes are unchanged after the trial;
- canonical hash before == canonical hash after.

The temporary workspace is then discarded.

## Decision

Allowed trial decisions:

```text
CANARY_PASS
CANARY_FAIL
```

`CANARY_PASS` requires all checks to pass:

- prior human/usefulness acceptance clear;
- EV retrieval isolated;
- canonical retrieval regression clear;
- negative-domain isolation clear;
- EV context stays inside configured budget;
- rollback verified;
- GenAI HOLD preserved;
- canary index remains exactly four records.

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

## GenAI boundary

GenAI/NIST is not part of this canary and remains:

```text
HOLD_FRESHNESS_REVIEW
```
