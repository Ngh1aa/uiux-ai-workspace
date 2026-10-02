# A50.5 — Human/Model-Assisted Knowledge Value Trial

Status: **MODEL-ASSISTED TRIAL IMPLEMENTED — INDEPENDENT HUMAN REVIEW PENDING**  
Date: **2026-10-02**

## Purpose

A50.5 moves beyond A50.4 deterministic retrieval/usefulness proxies by creating representative paired outputs for the same task/flow context **with** and **without** the currently retrieved seed knowledge.

It does not fabricate a human verdict. The checked-in state must remain blocked from corpus expansion until an independent reviewer records blind-first judgments.

Trial scope:

```text
model_assisted_blind_pair_trial_not_human_or_product_evidence
```

## Why this is not a live provider benchmark

The repository has a managed provider compatibility lane, but provider execution is opt-in and environment-dependent. A50.5 does not assume CI has API keys and does not silently convert a ChatGPT conversation into canonical runtime-provider evidence.

The paired samples in this phase are captured as advisory model-assisted artifacts from the user-directed ChatGPT session and declare:

```text
generation surface = user-directed ChatGPT session
model = GPT-5.6 Sol
runtime_provider_invoked = false
current_run_evidence = false
product_evidence = false
```

No chain-of-thought is stored.

## Representative cases

The trial covers the same three materially different domains used by A50.3/A50.4:

```text
Nova    / financial-services  / implementation
Lumen   / art-culture         / research
CENNEXT / industrial-services / research
```

For each case, the task/flow/stage context is fixed and two reviewable outputs are stored as `A` and `B`. One is the baseline condition without the retrieved Knowledge OS record; the other is the knowledge-assisted condition.

The knowledge label alternates across cases so the reviewer cannot assume that the same letter always means the same condition.

## Blinding model

A50.5 uses **procedural repository blinding**, not cryptographic blinding.

Review packet:

```text
benchmarks/knowledge-value-review-packet-v1.md
benchmarks/knowledge-value-trial-v1.json
```

Condition mapping:

```text
benchmarks/knowledge-value-trial-mapping-v1.json
```

A reviewer is instructed not to open the mapping until all blind scores/preferences/rationales are recorded.

Because the mapping exists in the same repository, this must never be described as cryptographically blind or tamper-proof.

## Human review rubric

A and B are scored independently from 0–2 on:

```text
correctness
specificity_actionability
relevance_noise
unsupported_claim_risk
decision_usefulness
```

Then the reviewer records:

```text
preferred_output = A | B | TIE | INSUFFICIENT
rationale
material_regression = true | false
reviewer
reviewed_at
```

The review ledger is:

```text
benchmarks/knowledge-value-human-reviews-v1.json
```

The checked-in A50.5 baseline contains three `PENDING` reviews with all human fields null. Tests reject fabricated reviewer data on a pending case.

## Governance states

Canonical evaluator:

```text
core/benchmarks/knowledge_value_trial.py
```

It can derive only:

```text
HOLD_PENDING_HUMAN
REVISE_BEFORE_EXPANSION
CONSIDER_EXPANSION
```

### HOLD_PENDING_HUMAN

Used whenever all three independent human reviews are not complete.

This is the required checked-in baseline for A50.5.

### REVISE_BEFORE_EXPANSION

Used after complete review when the conditions for a positive expansion recommendation are not met, including a material regression, a baseline preference, or insufficient decision-usefulness improvement.

This state does not automatically remove a seed record. It means the record/query/trial must be inspected before expanding the corpus.

### CONSIDER_EXPANSION

This is the strongest possible A50.5 recommendation, and it is still advisory.

The evaluator requires all reviews complete plus:

```text
material_regression_count = 0
baseline_preferred_count = 0
knowledge_preferred_count >= 2 of 3
knowledge condition strictly stronger on both:
  specificity_actionability
  decision_usefulness
in at least 2 of 3 cases
```

Even then:

```text
expand_allowed = false
auto_mutation_allowed = false
```

Adding a fourth record or new category still requires a separate explicit source/ownership review and repository change.

## Truth boundary

A50.5 can establish that:

- representative paired model outputs exist;
- task/flow/stage context is fixed per pair;
- the condition mapping is explicit and mixed across A/B labels;
- human-review fields are not fabricated;
- future complete human reviews can be converted into bounded governance states;
- corpus mutation remains impossible through this evaluator.

A50.5 does **not** establish that:

- the knowledge corpus improves real user outcomes;
- a human reviewer currently prefers the knowledge-assisted outputs;
- the model's hidden reasoning improved;
- the source facts are fresh for every future project;
- a runtime gate passed;
- a release is safe;
- the corpus should automatically expand.

## Implementation surfaces

```text
benchmarks/knowledge-value-trial-v1.json
benchmarks/knowledge-value-trial-mapping-v1.json
benchmarks/knowledge-value-human-reviews-v1.json
benchmarks/knowledge-value-review-packet-v1.md
core/benchmarks/knowledge_value_trial.py
scripts/validate_knowledge_value_trial.py
tests/test_knowledge_value_trial_a50.py
```

Main CI validates the checked-in trial before the full pytest suite.

## Completion boundary

A50.5 has two distinct completion levels:

### Engineering implementation complete

```text
paired artifacts captured
blind-first packet present
condition mapping present
human review ledger present
fail-closed evaluator implemented
governance regression in CI
full Factory regression green
```

### Human value verdict complete

Requires an independent human to review all three cases and commit the review ledger. Until then:

```text
human_review_complete = false
expansion_recommendation = HOLD_PENDING_HUMAN
```

This distinction prevents the engineering task from fabricating the human evidence it was explicitly designed to obtain.

## Next task after engineering merge

Perform the **A50.5 human review pass** using `knowledge-value-review-packet-v1.md`, then update only the review ledger first. Let the evaluator derive `CONSIDER_EXPANSION` or `REVISE_BEFORE_EXPANSION`; do not edit the mapping, seed records or threshold to fit the desired outcome.

If and only if the human verdict supports it, the next architecture task may define a bounded **A50.6 Corpus Expansion Proposal**. Vector search remains deferred until corpus breadth and deterministic retrieval actually justify it.
