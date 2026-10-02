# A50.2 — Bounded Knowledge Retrieval + Index

Status: **IMPLEMENTED ON FEATURE BRANCH — canonical corpus intentionally empty**  
Date: **2026-10-02**

## Purpose

A50.2 turns the A50.1 Knowledge OS metadata contract into a deterministic, bounded, provenance-bearing retrieval path without introducing vector search, a second Flow router, a new skill activation mechanism, project-memory writes, or evidence authority.

The execution order is explicit:

```text
Task / project context
→ canonical FlowSelectionDecision already exists
→ stage is known
→ KnowledgeQuery is built
→ canonical knowledge index is loaded
→ metadata filters/ranking run
→ content budget is applied
→ KnowledgeReasoningContext is attached as advisory context
```

Knowledge retrieval never runs early enough to choose the flow it will later inform.

## Canonical owners

```text
Declarative knowledge root
skills_UIUX/knowledge/

Canonical index
skills_UIUX/knowledge/index.json

Index schema
skills_UIUX/schemas/knowledge-index.schema.json

Record schema
skills_UIUX/schemas/knowledge-record.schema.json

Deterministic loader/retriever
uiux-factory/core/brain_os/knowledge_retrieval.py

Post-routing context adapter
uiux-factory/core/brain_os/adapters/knowledge_context.py
```

`skills_UIUX/knowledge/index.json` is currently empty on purpose. A50.2 proves the retrieval machinery with isolated benchmark fixtures rather than fabricating reusable product-design knowledge.

## Index contract

The v1 index contains only:

```json
{
  "schema_version": "knowledge-index.v1",
  "records": []
}
```

Future entries are repository-relative JSON metadata paths under `skills_UIUX/knowledge/records/`.

The loader fails closed when:

- the manifest is missing/malformed;
- unknown top-level keys are present;
- record paths are absolute, duplicate or escape the knowledge root;
- record metadata fails `KnowledgeRecord` validation;
- knowledge IDs are duplicated;
- `content_ref` resolves outside `skills_UIUX/knowledge/`;
- referenced content does not exist.

No filesystem search guesses missing records. Only the explicit index is canonical.

## Query contract

`KnowledgeQuery` carries:

```text
as_of
categories[]
domains[]
stages[]
tags[]
terms[]
limit
max_item_chars
max_total_chars
time_sensitive_max_age_days
```

Defaults:

```text
limit = 6
hard maximum limit = 12
max_item_chars = 4,000
max_total_chars = 12,000
time_sensitive_max_age_days = 30
```

All limits are explicit typed inputs so retrieval cannot silently expand context.

## Deterministic relevance policy

A50.2 does not use embeddings.

Hard filters:

1. category, when categories are supplied;
2. domain, when both query and record declare domain constraints;
3. stage, when both query and record declare stage constraints;
4. freshness for `time_sensitive` records.

Records with no domain/stage restrictions remain universal candidates.

Eligible records use transparent relevance points:

```text
matching domain = +12 each
matching stage  = +10 each
matching tag    = +6 each
matching term   = +2 each
category filter match = +4
```

Curatorial `confidence` is only a deterministic tie-breaker after relevance points. Final tie-break is stable knowledge ID ordering.

These points are retrieval ordering metadata only. They are not design-quality scores, evidence strength, gate confidence or product outcome metrics.

## Freshness policy

```text
evergreen
    no age exclusion

versioned
    version/provenance are preserved; no automatic age expiry in A50.2

time_sensitive
    updated_at must parse as an ISO date
    future-dated records fail safe
    age > query.time_sensitive_max_age_days is excluded
```

The time-sensitive age gate is repository freshness filtering, not external source re-verification. A record inside the age window may still require web/source verification for any current factual claim.

## Content and context budget

For every selected record:

1. full local content is read from `content_ref`;
2. full content SHA-256 is recorded;
3. delivery is capped by `max_item_chars` and remaining `max_total_chars`;
4. source vs delivered character counts are recorded;
5. `truncated=true` is explicit when content is clipped;
6. candidates beyond the record/context budget are reported in exclusions.

This avoids hidden context inflation and makes supplied knowledge reproducible.

## Post-routing adapter

`attach_knowledge_after_flow_selection(...)` requires an existing `FlowSelectionDecision` plus a concrete stage ID.

It derives bounded hints from canonical task context:

```text
domain
website_type
product_archetype
features
intent
```

Callers may additionally provide categories/tags/terms, but the adapter has no API to:

- select or replan a flow;
- activate a skill;
- change runtime authority;
- satisfy a gate;
- create trusted evidence;
- write project memory;
- finalize or release.

## Truth boundary

Every retrieval result and reasoning context remains:

```text
advisory_only = true
current_run_evidence = false
deterministic_metadata_first = true
vector_search_used = false
flow_effect = none
skill_activation_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

Knowledge can support a hypothesis or design rationale, but the resulting decision must still reference project/current evidence separately when evidence is required.

## Benchmark

A50.2 adds:

```text
benchmarks/knowledge-retrieval-v1.json
core/benchmarks/knowledge_retrieval_regression.py
scripts/validate_knowledge_retrieval_benchmark.py
```

Coverage includes:

- domain/stage-specific retrieval outranking universal context;
- unrelated domain exclusion;
- stale time-sensitive exclusion;
- hard category filtering;
- explicit character-budget truncation;
- bounded record count.

Benchmark scope is:

```text
deterministic_metadata_retrieval_not_product_or_runtime_evidence
```

A PASS proves only deterministic retrieval-policy regression behavior.

## Deliberate non-goals

A50.2 does not:

- seed a real Knowledge OS corpus;
- scrape/import external articles;
- live-verify time-sensitive facts;
- use embeddings or a vector DB;
- wire retrieval into every manager/provider stage automatically;
- make knowledge a gate input by itself;
- change FlowPlanner, skill routing, memory or release behavior.

## Completion criteria

A50.2 is complete when:

```text
canonical empty index exists
index and record paths fail closed
retrieval is post-flow-selection only
ranking/filtering are deterministic and explainable
freshness is explicit
record/item/context budgets are enforced
content hashes + truncation are preserved
no vector search is used
knowledge remains non-evidence/non-authoritative
retrieval benchmark runs in Main CI
full regression/dogfood remains green
```

## Next task

**A50.3 — Curated Seed Knowledge + Real-Project Retrieval Dogfood.**

Add a small human-curated seed corpus only from sources that can be traced and maintained, then dogfood retrieval against materially different projects such as Nova, Lumen and CENNEXT. Do not expand corpus breadth until retrieval usefulness and duplication risk are measured.
