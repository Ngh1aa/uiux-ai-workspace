# A50.8 — Knowledge Candidate Acceptance Trial

Status: **IMPLEMENTED / HUMAN REVIEW PENDING**  
Date: **2026-10-02**

## Purpose

A50.8 decides whether each A50.7 `KEEP_DRAFT` candidate is strong enough to enter a later **index trial**. It does not add either draft to the canonical Knowledge OS index.

The trial covers exactly:

```text
EdTech / LTI 1.3 + LTI Advantage
EV / OCPP 2.1 Edition 2
```

GenAI / NIST AI 600-1 remains outside this trial and stays `HOLD_FRESHNESS_REVIEW`.

## Inputs

A50.8 is downstream of the verified A50.7 draft report:

```text
A50.7
canonical index = 3
KEEP_DRAFT = 2
REVISE_DRAFT = 0
GenAI HOLD preserved
canonical_acceptance_allowed = false
```

Trial surfaces:

```text
benchmarks/knowledge-candidate-acceptance-trial-v1.json
benchmarks/knowledge-candidate-acceptance-mapping-v1.json
benchmarks/knowledge-candidate-acceptance-human-reviews-v1.json
benchmarks/knowledge-candidate-acceptance-review-packet-v1.md
core/benchmarks/knowledge_candidate_acceptance_trial.py
scripts/validate_knowledge_candidate_acceptance_trial.py
tests/test_knowledge_candidate_acceptance_trial_a50.py
```

## Model-assisted pair boundary

Each candidate has one baseline output and one knowledge-assisted output for the same task. The mapping is mixed across the two cases and stored separately from the review packet.

The pair generation is explicitly advisory:

```text
runtime_provider_invoked = false
product_evidence = false
current_run_evidence = false
```

No private chain-of-thought is stored.

The model-assisted samples are not independently reproducible provider runs and do not establish user validation, product quality, runtime truth or canonical corpus acceptance.

## Human review

The review packet must be scored before the mapping file is opened.

Dimensions:

```text
correctness
specificity_actionability
relevance_noise
unsupported_claim_risk
decision_usefulness
```

Score scale:

```text
0 = material weakness / harmful regression
1 = acceptable / no meaningful advantage
2 = materially stronger for the stated task
```

Allowed preferences:

```text
A
B
TIE
INSUFFICIENT
```

The repository must not fabricate review values. Until a human review is recorded, each candidate derives `HOLD`.

## Verdict policy

Allowed A50.8 verdicts are exactly:

```text
ACCEPT_FOR_INDEX_TRIAL
REVISE_DRAFT
HOLD
REJECT
```

Decision rules:

### `HOLD`

Use when:

- human review is still pending;
- reviewer returns `TIE`;
- reviewer returns `INSUFFICIENT`.

### `REVISE_DRAFT`

Use when:

- baseline is preferred; or
- knowledge-assisted output is preferred but does not simultaneously clear the acceptance guards.

### `REJECT`

Use when the independent human review reports a material regression.

### `ACCEPT_FOR_INDEX_TRIAL`

Requires all of the following for that candidate:

```text
human review complete
knowledge-assisted condition preferred
material_regression = false
knowledge correctness >= baseline correctness
knowledge unsupported_claim_risk >= baseline unsupported_claim_risk
knowledge specificity_actionability > baseline specificity_actionability
knowledge decision_usefulness > baseline decision_usefulness
```

This is intentionally stricter than `KEEP_DRAFT`.

## Critical authority boundary

Even a derived `ACCEPT_FOR_INDEX_TRIAL` does **not** mean canonical acceptance.

A50.8 always keeps:

```text
index_mutation_allowed = false
canonical_acceptance_allowed = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

`ACCEPT_FOR_INDEX_TRIAL` only permits a later task to design a controlled index-trial / acceptance implementation. It cannot edit `skills_UIUX/knowledge/index.json` itself.

## Current expected state

At initial merge, the human-review ledger is deliberately pending:

```text
reviewed = 0/2
ACCEPT_FOR_INDEX_TRIAL = 0
REVISE_DRAFT = 0
HOLD = 2
REJECT = 0
human_review_complete = false
```

This is the correct fail-closed state.

## Regression guards

Tests cover:

1. pending review → both candidates `HOLD`;
2. knowledge preference + joint usefulness + correctness/risk guards → `ACCEPT_FOR_INDEX_TRIAL`;
3. baseline preference → `REVISE_DRAFT`;
4. tie → `HOLD`;
5. material regression → `REJECT`;
6. even accepted synthetic fixtures cannot enable index mutation/canonical acceptance;
7. review packet does not expose the A/B condition mapping;
8. canonical index remains exactly three records and contains no draft paths.

## Next step

After A50.8 engineering verification, the user/human reviewer should score the blind packet:

```text
benchmarks/knowledge-candidate-acceptance-review-packet-v1.md
```

Only after both cases are scored should the mapping be opened and the human review ledger updated.

If one or both candidates derive `ACCEPT_FOR_INDEX_TRIAL`, the next task may create an explicit controlled index-trial proposal. It still must not silently promote drafts into the canonical corpus.
