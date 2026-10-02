# UIUX Knowledge OS — Declarative Ownership

Status: **A50.1 architecture contract**

`skills_UIUX/knowledge/` is the canonical home for reusable declarative product/design knowledge that should be retrieved as context but is **not** itself a skill, project memory, current-run evidence, runtime policy or release authority.

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

A knowledge record must never be promoted directly into trusted current-run evidence merely because it is curated or high-confidence.

## Taxonomy

A50.1 reserves seven top-level knowledge categories:

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

Taxonomy is metadata for retrieval. It must not hard-code flow/stage order or duplicate skill routing rules.

## Canonical metadata contract

Knowledge records must conform to:

```text
skills_UIUX/schemas/knowledge-record.schema.json
```

Required metadata includes:

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
```

Optional applicability metadata includes domains, stages and tags.

## Content ownership

A50.1 intentionally creates **no knowledge corpus yet**.

Future knowledge content should be authored as focused references under this directory and indexed/retrieved just-in-time. Do not bulk-copy existing `SKILL.md` bodies into knowledge files. When a topic is already procedural methodology in a skill, knowledge should link/reference the skill where appropriate rather than fork its instructions.

## Source and freshness

Every record requires provenance through `source_ref` and `source_kind`.

Freshness classifications:

```text
evergreen
versioned
time_sensitive
```

`confidence` describes the curatorial confidence in the reusable reference; it is **not** evidence confidence and cannot satisfy a runtime gate.

Time-sensitive knowledge must later be eligible for freshness filtering/revalidation before retrieval. A50.1 only defines the metadata; A50.2 will implement bounded retrieval policy.

## Retrieval boundary

A50.1 does not implement retrieval.

The future A50.2 retriever must:

- run after canonical task/flow context is known;
- retrieve only a bounded number of relevant knowledge records;
- preserve record/source provenance;
- respect stage/domain/context budgets;
- never select a flow, activate an unrouted skill, change authority, satisfy a gate or create trusted evidence;
- fail safe when knowledge is stale, missing or ambiguous.

## No vector-database requirement

A50.1 does not introduce a vector database. A deterministic metadata/index path should be proven first. Embeddings, if added later, may accelerate retrieval but must never become truth or override project/runtime evidence.

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
