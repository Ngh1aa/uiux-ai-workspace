# A50.5 — Human/Model-Assisted Knowledge Value Trial

Status: **ROUND 1 COMPLETE — REVISE BEFORE EXPANSION; ROUND 2 COMPLETE — CONSIDER EXPANSION**  
Date: **2026-10-02**

## Purpose

A50.5 moves beyond deterministic retrieval/usefulness proxies by comparing representative paired outputs for the same task/flow context **with** and **without** retrieved Knowledge OS context, then requiring a separate blind-first human review.

Trial scope:

```text
model_assisted_blind_pair_trial_not_human_or_product_evidence
```

The trial is governance evidence about knowledge usefulness only. It is not runtime evidence, product evidence, release evidence or proof that hidden model reasoning improved.

## Generation boundary

Paired samples are advisory artifacts from the user-directed ChatGPT session:

```text
generation surface = user-directed ChatGPT session
model = GPT-5.6 Sol
runtime_provider_invoked = false
current_run_evidence = false
product_evidence = false
```

No private chain-of-thought is stored.

## Representative cases

```text
Nova    / financial-services  / implementation
Lumen   / art-culture         / research
CENNEXT / industrial-services / research
```

Each case has a baseline condition and a knowledge-assisted condition presented as A/B. The mapping is stored separately. Blinding is **procedural repository blinding**, not cryptographic blinding.

Round-one surfaces:

```text
benchmarks/knowledge-value-trial-v1.json
benchmarks/knowledge-value-trial-mapping-v1.json
benchmarks/knowledge-value-human-reviews-v1.json
benchmarks/knowledge-value-review-packet-v1.md
```

Round-two surfaces:

```text
benchmarks/knowledge-value-trial-v2.json
benchmarks/knowledge-value-trial-mapping-v2.json
benchmarks/knowledge-value-human-reviews-v2.json
benchmarks/knowledge-value-review-packet-v2.md
```

## Human review rubric

A and B are scored independently from 0–2 on:

```text
correctness
specificity_actionability
relevance_noise
unsupported_claim_risk
decision_usefulness
```

The reviewer then records:

```text
preferred_output = A | B | TIE | INSUFFICIENT
rationale
material_regression = true | false
reviewer
reviewed_at
```

## Governance evaluator

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

A positive expansion recommendation requires all reviews complete plus:

```text
material_regression_count = 0
baseline_preferred_count = 0
knowledge_preferred_count >= 2 of 3
knowledge condition strictly stronger on both:
  specificity_actionability
  decision_usefulness
in at least 2 of 3 cases
```

The evaluator exposes the latter count as:

```text
joint_usefulness_win_count
```

Even `CONSIDER_EXPANSION` remains advisory:

```text
expand_allowed = false
auto_mutation_allowed = false
```

## Round-one human result

The blind-first human review was completed and committed without changing the mapping or threshold.

After unblinding:

```text
Nova     knowledge condition = B
Lumen    knowledge condition = A
CENNEXT  knowledge condition = B
```

Recorded preferences:

```text
Nova     → B / knowledge preferred
Lumen    → A / knowledge preferred
CENNEXT  → TIE
```

Derived counts:

```text
knowledge_preferred_count = 2
baseline_preferred_count = 0
tie_count = 1
material_regression_count = 0
joint_usefulness_win_count = 1
```

Therefore the canonical round-one result remains:

```text
REVISE_BEFORE_EXPANSION
```

## Round-two revision trial result

A50.5R revised only the two underperforming existing records (Nova and CENNEXT), preserved their round-one baselines exactly, kept Lumen as the unchanged control, mixed A/B labels again, and retained the same governance threshold.

The reviewer completed all three round-two blind judgments before opening the v2 mapping.

After unblinding:

```text
Nova     knowledge condition = A
Lumen    knowledge condition = B
CENNEXT  knowledge condition = A
```

Recorded preferences:

```text
Nova     → A / knowledge preferred
Lumen    → B / knowledge preferred
CENNEXT  → A / knowledge preferred
```

Derived counts:

```text
human_review_complete = true
reviewed_case_count = 3
knowledge_preferred_count = 3
baseline_preferred_count = 0
tie_count = 0
insufficient_count = 0
material_regression_count = 0
joint_usefulness_win_count = 3
```

The unchanged evaluator therefore derives:

```text
CONSIDER_EXPANSION
```

This means the revision crossed the governance threshold; it does **not** mean the corpus may mutate automatically.

## Truth boundary

A50.5/A50.5R establishes that:

- paired advisory outputs exist;
- the condition mappings are explicit and mixed across A/B labels;
- human review provenance is recorded separately;
- round one remains immutable historical `REVISE_BEFORE_EXPANSION` evidence;
- round two is complete and derives `CONSIDER_EXPANSION` under the unchanged threshold;
- the round-two knowledge condition is preferred 3/3 with 3/3 joint specificity/actionability + decision-usefulness wins and no material regressions;
- corpus mutation remains impossible through the evaluator.

A50.5/A50.5R does **not** establish that:

- real user outcomes improved;
- hidden model reasoning improved;
- source facts remain current forever;
- a runtime/release gate passed;
- an arbitrary fourth record is safe or useful;
- vector search is justified.

## Next task

Open **A50.6 — Corpus Expansion Proposal**.

A50.6 is a proposal/governance phase, not automatic corpus growth. Candidate records must receive explicit source, ownership, duplication, freshness, scope and retrieval-value review before any later accepted implementation mutates the canonical index.

Vector search remains deferred.
