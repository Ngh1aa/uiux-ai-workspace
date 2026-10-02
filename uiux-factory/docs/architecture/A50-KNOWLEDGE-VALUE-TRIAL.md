# A50.5 — Human/Model-Assisted Knowledge Value Trial

Status: **ROUND 1 COMPLETE — REVISE BEFORE EXPANSION**  
Date: **2026-10-02**

## Purpose

A50.5 moves beyond deterministic retrieval/usefulness proxies by comparing representative paired outputs for the same task/flow context **with** and **without** retrieved Knowledge OS context, then requiring a separate blind-first human review.

Trial scope:

```text
model_assisted_blind_pair_trial_not_human_or_product_evidence
```

The trial is governance evidence about knowledge usefulness only. It is not runtime evidence, product evidence, release evidence or proof that hidden model reasoning improved.

## Generation boundary

Round-one paired samples were captured as advisory artifacts from the user-directed ChatGPT session:

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

Canonical round-one surfaces:

```text
benchmarks/knowledge-value-trial-v1.json
benchmarks/knowledge-value-trial-mapping-v1.json
benchmarks/knowledge-value-human-reviews-v1.json
benchmarks/knowledge-value-review-packet-v1.md
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
```

However, only Lumen had the knowledge-assisted condition strictly stronger on **both** `specificity_actionability` and `decision_usefulness`. Nova's knowledge condition improved conceptual correctness but lost some decision usefulness versus the baseline; CENNEXT's knowledge condition improved conceptual precision but tied overall because the baseline was more buyer-actionable.

Therefore the canonical round-one result is:

```text
REVISE_BEFORE_EXPANSION
```

The threshold was not weakened to fit the result.

## Revision implication

Round one identified two bounded revision targets:

```text
Nova
  preserve locale/currency correctness
  + shared formatter boundary
  + explicit fallback behavior
  + concrete QA matrix

CENNEXT
  preserve technical claim taxonomy
  + buyer decision path
  + traceable proof modules
  + customer approval / repair-vs-replace decision support
```

Lumen remains the control because its knowledge-assisted output already met the combined specificity/actionability + decision-usefulness threshold.

These changes are implemented and re-tested separately in **A50.5R — Knowledge Revision Pass / Round 2**. Round-one files remain immutable historical evidence of the prior governance outcome.

## Truth boundary

A50.5 establishes that:

- paired advisory outputs exist;
- the condition mapping is explicit and mixed across A/B labels;
- human review provenance is recorded separately;
- the round-one human verdict is complete;
- the round-one result is `REVISE_BEFORE_EXPANSION`;
- corpus mutation remains impossible through the evaluator.

A50.5 does **not** establish that:

- real user outcomes improved;
- hidden model reasoning improved;
- the corpus should automatically expand;
- a runtime/release gate passed;
- source facts remain current forever.

## Next task

Proceed through **A50.5R round-two blind review**. Only if the unchanged evaluator derives `CONSIDER_EXPANSION` after a complete round-two human review should a separate **A50.6 Corpus Expansion Proposal** be opened. Vector search remains deferred.
