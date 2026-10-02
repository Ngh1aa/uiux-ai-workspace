# A50.8 — Knowledge Candidate Acceptance Trial

Status: **HUMAN REVIEW COMPLETE / VERDICTS DERIVED**  
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

The review packet was scored before the mapping file was opened.

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

The repository does not fabricate review values. The canonical human ledger now records the completed blind-first review.

## Unblinded mapping and human result

The mapping was opened only after both cases were scored:

```text
EdTech / LTI: knowledge = A, baseline = B
EV / OCPP:    knowledge = B, baseline = A
```

Human result:

```text
EdTech preferred output = A (knowledge)
EV preferred output     = B (knowledge)
material regressions    = 0
reviewed                 = 2/2
human_review_complete   = true
```

### EdTech / LTI scores

```text
A knowledge:
  correctness               2
  specificity_actionability 2
  relevance_noise           2
  unsupported_claim_risk    2
  decision_usefulness       1

B baseline:
  correctness               1
  specificity_actionability 1
  relevance_noise           2
  unsupported_claim_risk    2
  decision_usefulness       1
```

The reviewer preferred A overall because it names the LTI integration/service boundaries, separates launch from NRPS/AGS/Deep Linking semantics and makes system authority explicit. However, its decision usefulness did not exceed B because it mostly says what the team must define rather than supplying concrete unavailable/permission/error/recovery states. Therefore the strict joint-usefulness acceptance guard is not satisfied.

### EV / OCPP scores

```text
A baseline:
  correctness               1
  specificity_actionability 1
  relevance_noise           2
  unsupported_claim_risk    2
  decision_usefulness       1

B knowledge:
  correctness               2
  specificity_actionability 2
  relevance_noise           2
  unsupported_claim_risk    2
  decision_usefulness       2
```

The reviewer preferred B because it ties visible charging states to station/backend observations, includes explicit unknown/awaiting-confirmation handling, keeps protocol/session/payment truth separate and gates optional OCPP capabilities behind deployment evidence.

The review initially flagged the OCPP 2.1 feature list for source verification. On 2026-10-02 the official Open Charge Alliance OCPP material was checked and confirms support for ISO 15118-20, bidirectional/V2X functionality, DER control and improved smart charging in OCPP 2.1. This source check supports retaining the human `correctness = 2` score; it does not convert the trial into product/runtime evidence.

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

## Derived canonical verdicts

The unchanged evaluator derives:

```text
EdTech / LTI → REVISE_DRAFT
EV / OCPP    → ACCEPT_FOR_INDEX_TRIAL
```

Why:

```text
EdTech:
  correctness guard = clear
  unsupported-claim-risk guard = clear
  specificity win = true
  decision-usefulness win = false
  joint usefulness win = false

EV:
  correctness guard = clear
  unsupported-claim-risk guard = clear
  specificity win = true
  decision-usefulness win = true
  joint usefulness win = true
```

## Critical authority boundary

Even the EV `ACCEPT_FOR_INDEX_TRIAL` verdict does **not** mean canonical acceptance.

A50.8 always keeps:

```text
index_mutation_allowed = false
canonical_acceptance_allowed = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

`ACCEPT_FOR_INDEX_TRIAL` only permits a later task to design a controlled index-trial / acceptance implementation. It cannot edit `skills_UIUX/knowledge/index.json` itself.

The canonical Knowledge OS index therefore remains exactly three records after A50.8.

## Regression guards

Tests cover:

1. canonical completed review → EdTech `REVISE_DRAFT`, EV `ACCEPT_FOR_INDEX_TRIAL`;
2. knowledge preference + joint usefulness + correctness/risk guards → `ACCEPT_FOR_INDEX_TRIAL`;
3. baseline preference → `REVISE_DRAFT`;
4. tie → `HOLD`;
5. material regression → `REJECT`;
6. even accepted synthetic fixtures cannot enable index mutation/canonical acceptance;
7. review packet does not expose the A/B condition mapping;
8. canonical index remains exactly three records and contains no draft paths.

## Next step

The next task must split by candidate instead of treating the two drafts symmetrically:

```text
EdTech / LTI → revision pass before another acceptance trial
EV / OCPP    → controlled index-trial proposal
GenAI / NIST → remain HOLD_FRESHNESS_REVIEW
```

Do not add EV to `skills_UIUX/knowledge/index.json` merely because it earned `ACCEPT_FOR_INDEX_TRIAL`. A separate controlled index-trial task must define rollback, retrieval regression, cross-domain isolation and acceptance evidence first. Vector search remains deferred.
