# A50.4 — Knowledge Usefulness Evaluation + Corpus Governance

Status: **IMPLEMENTED ON FEATURE BRANCH — corpus expansion remains blocked**  
Date: **2026-10-02**

## Purpose

A50.4 evaluates whether the three A50.3 seed records add bounded, project-relevant context without duplicating existing skill methodology or increasing retrieval noise.

It deliberately does **not** claim to measure model reasoning quality, human usefulness, usability, product outcomes or design quality.

The benchmark scope is:

```text
deterministic_context_usefulness_proxy_not_model_reasoning_or_product_evidence
```

## Evaluation dimensions

Each seed is evaluated independently on five named usefulness boundaries plus context size:

```text
actionable_delta
    Does the retrieved content contain the project-relevant domain concepts that were absent from the generic task/profile context?

domain_specificity
    Does the project retrieve exactly the intended domain record?

skill_duplication_clear
    Does the knowledge avoid exact substantive-line duplication with the related canonical skill methodology?

retrieval_noise_clear
    Are the two unrelated seed records excluded by domain mismatch?

provenance_clear
    Does the record preserve HTTPS source provenance, version/date metadata and no evidence/gate/release authority?

context_budget_clear
    Is the delivered context non-trivial but bounded to the existing per-item budget?
```

These are deterministic proxies. They are intentionally separate rather than collapsed into an overall “knowledge quality score”.

## With vs without knowledge interpretation

The deterministic comparison is:

```text
WITHOUT KNOWLEDGE
canonical task/flow/stage context only

WITH KNOWLEDGE
same canonical task/flow/stage context
+ exactly one retrieved domain record
+ explicit provenance / context chars / exclusions
```

A50.4 checks whether that additional context carries concrete domain concepts and remains isolated from unrelated records. It does not run an LLM twice and does not infer that the model would necessarily reason better.

## Current seed decisions

Expected governance decisions are:

```text
Nova financial seed   → KEEP
Lumen cultural seed   → KEEP
CENNEXT industrial seed → KEEP
```

A record derives `KEEP` only when all deterministic boundaries pass. If any boundary fails, the evaluator derives `REVISE`.

`REMOVE` is available to later governance changes but is not automatically inferred from one deterministic failure because removal should distinguish a bad record from a bad benchmark/query.

## Duplication boundary

A50.4 compares substantive normalized lines from knowledge content with related active skills. Exact long-line duplication is rejected.

This is a conservative duplication proxy, not semantic-plagiarism detection. A record can still discuss the same domain as a skill as long as it contributes reference facts instead of copying the skill's procedure.

Related owners checked in v1 include:

```text
financial-product-intelligence
asset-media-and-art-direction
trust-credibility-and-transparency
website-audit-and-redesign
```

## Corpus expansion governance

A50.4 explicitly forbids `EXPAND` as a benchmark decision.

Allowed record decisions:

```text
KEEP
REVISE
REMOVE
```

Global governance remains:

```text
expand_allowed = false
```

Reason: deterministic checks can prove retrieval fit, bounded context, provenance and duplication/noise boundaries, but cannot prove model reasoning improvement or human usefulness.

Before adding record four or populating broader categories, a separate human/model-assisted usefulness trial must compare representative work with vs without the seed and record whether the context changes decisions or output quality in a useful, non-redundant way.

## Benchmark implementation

```text
benchmarks/knowledge-usefulness-v1.json
core/benchmarks/knowledge_usefulness_regression.py
scripts/validate_knowledge_usefulness_benchmark.py
tests/test_knowledge_usefulness_a50.py
```

Main CI runs the usefulness benchmark after retrieval/project-dogfood benchmarks and before full pytest.

## Truth boundary

A PASS means only:

```text
expected domain record retrieved
required domain concepts present
no exact substantive-line skill duplication detected
unrelated records excluded
source/version provenance present
context remains bounded
```

It does **not** mean:

```text
model reasoning improved
human reviewer preferred the result
usability improved
product metrics improved
source facts are current for every future task
the corpus should expand
```

## Completion criteria

A50.4 is complete when:

```text
all 3 seed records receive deterministic KEEP
all usefulness dimensions pass independently
expand_allowed remains false
benchmark is in Main CI
full Factory regression remains green
real-project dogfood remains green when triggered
```

## Next task

**A50.5 — Human/Model-Assisted Knowledge Value Trial.**

Use a small set of representative design/product reasoning tasks to compare outputs with and without retrieved knowledge under the same task/flow context. Human review should judge whether the context materially improves correctness, specificity or decision quality without adding noise. Only that phase may recommend `EXPAND`, and any expansion still requires explicit source/ownership review.
