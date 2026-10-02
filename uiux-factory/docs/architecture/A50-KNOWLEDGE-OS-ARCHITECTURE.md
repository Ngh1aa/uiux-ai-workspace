# A50.1 — Knowledge OS Architecture

Status: **IMPLEMENTED ON FEATURE BRANCH — retrieval intentionally not implemented**  
Date: **2026-10-02**

## Purpose

A50.1 introduces the architecture contract for reusable Product Design / UX knowledge without creating a parallel execution system, a second skill corpus, a project-memory store, or a new evidence authority.

The core distinction is:

```text
skills_UIUX/<skill>/SKILL.md
    owns procedural methodology: HOW to perform work

skills_UIUX/knowledge/
    owns reusable declarative knowledge: WHAT principles/reference context may inform work

core/brain_os/memory_contracts.py + core/memory/
    own project/run history: WHAT happened before in this project

core/runtime/flow_os/evidence.py + core/provenance/ + uiux-factory/qa/
    own current observed truth: WHAT is supported in this run
```

Knowledge may inform reasoning. It does not become evidence, memory, routing policy, approval, gate status or release authority.

## Canonical owners

A50.1 establishes:

```text
Declarative knowledge owner
skills_UIUX/knowledge/

Knowledge metadata schema
skills_UIUX/schemas/knowledge-record.schema.json

Typed Brain read model
uiux-factory/core/brain_os/knowledge_contracts.py
```

The Python contract is a typed read/view layer over the declarative owner. It is not a second knowledge database.

## Taxonomy

Seven top-level categories are reserved:

```text
foundations
product
research
management
domain
pattern
platform
```

They intentionally describe retrieval dimensions rather than workflow order.

Typical topic families:

| Category | Examples |
| --- | --- |
| foundations | UX, interaction, IA, visual design, cognition, accessibility |
| product | discovery, strategy, prioritization, experimentation, metrics |
| research | interviews, usability, surveys, analytics interpretation, synthesis |
| management | critique, facilitation, stakeholder alignment, design operations, governance |
| domain | fintech, ecommerce, B2B, AI software, EdTech, mobility, travel, culture, industrial services |
| pattern | onboarding, checkout, dashboards, search, forms, empty/error states |
| platform | web, mobile, desktop, platform interaction constraints |

Taxonomy must not duplicate Flow OS routing logic. `applicable_stages`, `applicable_domains` and `tags` are retrieval metadata only.

## KnowledgeRecord truth boundary

Each record carries provenance and freshness metadata:

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
applicable_domains[]
applicable_stages[]
tags[]
```

Hard truth flags are fixed:

```text
advisory_only = true
current_run_evidence = false
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

`confidence` means curatorial confidence in the reusable reference. It is not runtime evidence confidence and cannot satisfy a gate.

## Source classes

A50.1 supports four source kinds:

```text
repo_reference
external_reference
standard
human_curated
```

and three freshness classes:

```text
evergreen
versioned
time_sensitive
```

A future retriever must treat freshness as policy input. Time-sensitive records cannot be assumed current merely because they exist in the repository.

## Memory and evidence separation

Knowledge records reject Brain-memory IDs and current-run evidence IDs as their content/source ownership.

This prevents architecture drift such as:

```text
historical decision → copied into knowledge → treated as universal principle
runtime screenshot/evidence → copied into knowledge → later reused as if still current
```

Project-specific decisions belong in typed memory. Current observations belong in evidence. Reusable knowledge must have its own source provenance.

## Skill methodology separation

A50.1 explicitly forbids bulk-copying `SKILL.md` bodies into the Knowledge OS.

When a skill already owns procedural guidance, a knowledge item may reference that skill but must not fork its procedure into a second canonical methodology. This avoids contradictory instructions, stale duplicate checklists and ambiguous ownership.

## Retrieval boundary

A50.1 does **not** implement retrieval.

A50.2 may add a bounded deterministic retrieval layer only after canonical task/flow context is known. That layer must:

1. preserve source/version/freshness provenance;
2. retrieve a bounded number of records under context budget;
3. respect domain/stage relevance without changing canonical flow selection;
4. never activate unrouted skills;
5. never mutate authority, gate, evidence or release state;
6. fail safe on missing, stale or ambiguous knowledge;
7. expose exactly what records were supplied to reasoning;
8. keep project truth and current evidence higher-authority than generic reusable knowledge.

## Vector database decision

No vector database is required in A50.1.

The intended sequence is:

```text
metadata contract
→ deterministic index/retrieval
→ retrieval benchmark
→ real-project dogfood
→ only then consider semantic/vector acceleration if justified
```

Embeddings may later improve recall but can never become truth or override provenance.

## Runtime and authority effects

A50.1 introduces no lifecycle execution path and no runtime mutation.

It does not:

```text
select/replan Flow OS
activate skills
run provider tools
create trusted evidence
satisfy gates
approve human checkpoints
finalize worktrees
deploy/release
```

## Regression guards

`tests/test_knowledge_architecture_a50.py` protects:

- canonical owner declarations;
- taxonomy parity between Python and JSON schema;
- `retrieval_implemented=false` and `vector_database_required=false` in A50.1;
- knowledge-vs-memory field separation;
- rejection of Brain-memory/current-evidence ownership refs;
- no `SKILL.md` methodology fork inside `skills_UIUX/knowledge/`.

## A50.1 completion criteria

A50.1 is complete when:

```text
schema exists and matches typed contract
seven-category taxonomy is frozen for v1
skill / knowledge / memory / evidence ownership is explicit
knowledge is advisory-only and release-neutral
memory/evidence refs cannot become knowledge ownership
no corpus is silently invented
no retrieval/vector runtime is introduced
architecture drift tests pass
main CI and A20 remain green
```

## Next task

**A50.2 — Bounded Knowledge Retrieval + Index.**

Implement deterministic metadata-first retrieval over future knowledge records with explicit freshness/context budgets and retrieval provenance. Do not add vector search until deterministic retrieval has a benchmark and real-project dogfood evidence.
