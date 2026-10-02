# UIUX Knowledge OS — Declarative Ownership

Status: **A50.2 bounded deterministic retrieval implemented**

`skills_UIUX/knowledge/` is the canonical home for reusable declarative product/design knowledge that may be retrieved as context but is **not** itself a skill, project memory, current-run evidence, runtime policy or release authority.

## Boundary: skill vs knowledge vs memory vs evidence

```text
SKILL
= how to perform work
= procedures, methods, checklists, execution guidance
= canonical owner: skills_UIUX/<skill>/SKILL.md

KNOWLEDGE
= reusable principles, factual/domain context, stable patterns and reference material
= canonical owner: skills_UIUX/knowledge/

MEMORY
= what happened in a particular project/run: rationale, hypotheses, decisions, recurring history
= canonical owners: core/brain_os/memory_contracts.py + core/memory/

EVIDENCE
= current observed/provenance-bearing truth used to support gates/evaluation
= canonical owners: core/runtime/flow_os/evidence.py + core/provenance/ + uiux-factory/qa/
```

A knowledge record must never be promoted directly into trusted current-run evidence merely because it is curated, retrieved or high-confidence.

## Directory contract

```text
skills_UIUX/knowledge/
├── README.md
├── index.json              # canonical metadata index
├── records/                # future KnowledgeRecord JSON metadata
└── content/                # future focused reusable knowledge content
```

`index.json` conforms to `skills_UIUX/schemas/knowledge-index.schema.json` and contains only relative paths to record metadata. The current canonical index is intentionally empty until knowledge content is actually curated.

Each metadata record conforms to `skills_UIUX/schemas/knowledge-record.schema.json`. `content_ref` must resolve to content inside `skills_UIUX/knowledge/`; traversal outside this root fails closed.

## Taxonomy

Seven top-level knowledge categories are reserved:

```text
foundations
product
research
management
domain
pattern
platform
```

Suggested topic families:

- `foundations`: UX, interaction, IA, visual design, cognition, accessibility.
- `product`: discovery, strategy, prioritization, experimentation, measurement.
- `research`: interviews, usability, surveys, analytics interpretation, synthesis principles.
- `management`: critique, facilitation, stakeholder alignment, design operations, governance.
- `domain`: fintech, ecommerce, B2B, AI software, EdTech, mobility, travel, culture, industrial services.
- `pattern`: onboarding, checkout, dashboard, search, forms, empty/error states, progressive disclosure.
- `platform`: web, mobile, desktop and platform-specific interaction constraints.

Taxonomy is retrieval metadata. It must not hard-code flow/stage order or duplicate skill routing rules.

## Canonical metadata contract

Required record metadata includes:

```text
id
title
category
topic
summary
content_ref
source_ref
source_kind
version
updated_at
freshness
confidence
advisory_only = true
current_run_evidence = false
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

Optional applicability metadata includes domains, stages and tags.

## Source and freshness

Every record requires provenance through `source_ref` and `source_kind`.

Freshness classifications:

```text
evergreen
versioned
time_sensitive
```

`confidence` describes curatorial confidence in the reusable reference; it is **not** evidence confidence and cannot satisfy a runtime gate.

A50.2 applies a deterministic age gate to `time_sensitive` records using query `as_of` plus an explicit `time_sensitive_max_age_days` budget. This is only repository freshness filtering; it is **not** live web re-verification of the upstream source.

## Retrieval contract

Canonical implementation:

```text
uiux-factory/core/brain_os/knowledge_retrieval.py
uiux-factory/core/brain_os/adapters/knowledge_context.py
```

Retrieval is:

- metadata-first and deterministic;
- executed only after a canonical `FlowSelectionDecision` exists;
- hard-filtered by category/domain/stage when those constraints are supplied;
- ranked by explicit domain/stage/tag/term matches with confidence only as a deterministic tie-breaker;
- bounded by record count, per-item characters and total context characters;
- provenance-bearing through index hash, record path, source reference and full content SHA-256;
- explicit about truncation and exclusions;
- vector-free.

Retrieval can never select/replan a flow, activate an unrouted skill, write project memory, change authority, satisfy a gate, create trusted evidence, finalize a worktree or authorize release.

## Context budget defaults

A50.2 defaults:

```text
record limit = 6
hard record limit = 12
max chars per item = 4,000
max total chars = 12,000
time-sensitive max age = 30 days
```

Callers may reduce or explicitly adjust budgets within the typed bounds. Retrieved content is truncated deterministically when a context budget requires it, and that truncation is surfaced in the result.

## No vector database

A50.2 intentionally uses no vector database or embeddings. Semantic acceleration remains deferred until deterministic retrieval has stable benchmark coverage plus useful real-project dogfood against a curated corpus.

## Content ownership

The canonical index is currently empty. A50.2 does **not** invent knowledge content merely to make retrieval appear populated.

Future knowledge content should be authored as focused references under this directory. Do not bulk-copy existing `SKILL.md` bodies into knowledge files. When a topic is already procedural methodology in a skill, knowledge should link/reference the skill rather than fork its instructions.

## Governance

A knowledge item can inform a design/product decision, but material decisions must still distinguish:

```text
reusable knowledge
vs project truth
vs inference/hypothesis
vs current evidence
vs human decision
```

This separation is a hard Brain OS architecture boundary.
