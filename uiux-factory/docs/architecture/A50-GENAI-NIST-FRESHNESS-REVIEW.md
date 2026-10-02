# A50.14 — GenAI/NIST Freshness Review

Status: **KEEP HOLD / NO DRAFT / NO INDEX MUTATION**  
Date: **2026-10-02**

## Purpose

Re-evaluate the held `a50-6-genai-nist` candidate against current official NIST source truth without creating a draft, canonical record, canary or promotion path.

## Official source findings

Checked on 2026-10-02:

- NIST AI 600-1 remains the official `Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile` resource.
- NIST's publication page still identifies it as the cross-sector Generative AI companion/profile for AI RMF 1.0.
- NIST states AI RMF 1.0 is being revised.
- NIST AIRC states the revised version is still in progress.

Therefore the existing candidate version caveat remains accurate:

```text
NIST-AI-600-1-2024-with-2026-framework-revision-caveat
```

but the framework dependency is not stable enough to open drafting/canonicalization yet.

## Decision

```text
KEEP_HOLD_FRESHNESS_REVIEW
```

The candidate remains useful in principle, but freshness risk remains `HIGH` while AI RMF 1.0 revision is active.

## Re-review trigger

Re-open freshness review when NIST either:

1. publishes a revised AI RMF replacing 1.0; or
2. explicitly states that the active AI RMF revision is complete/stable enough for profile-context reuse.

## Non-mutation boundary

A50.14 requires the current five-record A50.13 canonical topology to remain unchanged and keeps all of these false:

```text
draft_creation_allowed
canonical_record_creation_allowed
index_mutation_allowed
acceptance_trial_allowed
canary_allowed
promotion_allowed
vector_search_change_allowed
product_evidence
```

The GenAI candidate must remain unindexed with no canonical GenAI assets.

## Executable truth

```text
benchmarks/knowledge-genai-nist-freshness-review-v1.json
core/benchmarks/knowledge_genai_nist_freshness_review.py
scripts/validate_knowledge_genai_nist_freshness_review.py
tests/test_knowledge_genai_nist_freshness_review_a50.py
```

The validator fails closed if the historical candidate HOLD drifts, five-record baseline changes unexpectedly, GenAI assets appear, mutation authority is enabled, the re-review trigger disappears, or final-owner-review delegation boundaries change.

Final retrospective owner review remains deferred until the broader workspace upgrade is complete.
