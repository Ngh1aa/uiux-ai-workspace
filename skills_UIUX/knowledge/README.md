# UIUX Knowledge OS — Declarative Ownership

Status: **A50.10C canonical corpus — 4 curated domain records**

`skills_UIUX/knowledge/` is the canonical home for reusable declarative product/design knowledge that may be retrieved as context but is **not** itself a skill, project memory, current-run evidence, runtime policy or release authority.

## Boundary

```text
SKILL
= how to perform work
= procedures, methods, checklists, execution guidance
= owner: skills_UIUX/<skill>/SKILL.md

KNOWLEDGE
= reusable principles, domain/reference context and stable patterns
= owner: skills_UIUX/knowledge/

MEMORY
= what happened in a particular project/run
= owners: core/brain_os/memory_contracts.py + core/memory/

EVIDENCE
= current observed/provenance-bearing truth used by runtime evaluation/gates
= owners: core/runtime/flow_os/evidence.py + core/provenance/ + uiux-factory/qa/
```

Retrieved knowledge remains advisory. It never becomes trusted current-run evidence merely because it is curated, retrieved or high-confidence.

## Directory contract

```text
skills_UIUX/knowledge/
├── README.md
├── index.json
├── records/
│   ├── financial-currency-locale-formatting.json
│   ├── cultural-object-metadata-rights-iiif.json
│   ├── industrial-motor-system-claims-doe.json
│   └── ev-charging-ocpp-transaction-semantics.json
└── content/
    ├── financial-currency-locale-formatting.md
    ├── cultural-object-metadata-rights-iiif.md
    ├── industrial-motor-system-claims-doe.md
    └── ev-charging-ocpp-transaction-semantics.md
```

`index.json` conforms to `skills_UIUX/schemas/knowledge-index.schema.json`; every record conforms to `skills_UIUX/schemas/knowledge-record.schema.json`. `content_ref` must stay inside this knowledge root.

Drafts, revisions and governance artifacts remain outside the canonical `records/` + `content/` pair and are preserved for provenance/history.

## Canonical corpus

A50.3 started with a deliberately small three-record seed. A50.10C promotes the independently trialed EV/OCPP candidate, producing four canonical records:

| Domain | Record | Primary/authoritative source |
| --- | --- | --- |
| `financial-services` | locale- and currency-aware amount formatting | Unicode CLDR / UTS #35 Part 3 |
| `art-culture` | cultural-object metadata, required statements, rights and provider concepts | IIIF Presentation API 3.0 |
| `industrial-services` | motor-system context for repair/efficiency/performance claims | U.S. Department of Energy Motor Systems |
| `mobility-ev` | OCPP 2.1 transaction and charging-system semantics | Open Charge Alliance OCPP 2.1 Edition 2 / Errata 2026-06 |

The repository stores concise paraphrased reference material. It does not copy long source passages or turn the source into project evidence.

## Why these records belong here

The corpus contains domain/reference facts rather than workflow instructions. Existing skill methodology remains canonical elsewhere, including financial workflow/state/evidence reasoning, media/art-direction procedure, accessibility workflow and generic state/error recovery.

Knowledge content must not add `SKILL.md` files or fork procedural sections such as `Workflow`, `Acceptance criteria` or numbered execution steps from active skills.

## Taxonomy

Seven top-level categories remain reserved:

```text
foundations
product
research
management
domain
pattern
platform
```

The current canonical corpus uses only `domain`. Taxonomy is retrieval metadata and must not duplicate Flow OS routing.

## Required truth flags

Every record remains fixed to:

```text
advisory_only = true
current_run_evidence = false
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

`confidence` is curatorial confidence in the reusable reference, not evidence confidence.

## Retrieval

Canonical implementation:

```text
uiux-factory/core/brain_os/knowledge_retrieval.py
uiux-factory/core/brain_os/adapters/knowledge_context.py
```

Retrieval is metadata-first, deterministic, post-flow-selection, provenance-bearing, context-bounded and vector-free. Domain and stage constraints are hard filters when both query and record declare them. Every delivered hit preserves source/content provenance and explicit truncation state.

Current defaults:

```text
record limit = 6
hard record limit = 12
max chars per item = 4,000
max total chars = 12,000
time-sensitive max age = 30 days
```

## Active retrieval regression

Main CI validates the original project profiles plus the promoted EV domain:

```text
Nova     → financial-services → financial currency/locale record only
Lumen    → art-culture        → IIIF cultural-object record only
CENNEXT  → industrial-services → DOE motor-system record only
EV/OCPP  → mobility-ev        → OCPP transaction/system semantics record only
```

For each positive domain, the other three canonical records must be excluded by domain mismatch. EdTech and AI-software negative-domain checks must return no canonical hit. This tests retrieval precision and isolation; it is not product-quality or user-validation evidence.

## Source freshness

- CLDR record is pinned to stable 48.2 / UTS #35 Part 3.
- IIIF record is pinned to Presentation API 3.0.
- DOE record uses the Motor Systems reference surface curated on 2026-10-02.
- OCPP record is pinned to OCPP 2.1 Edition 2 / Errata 2026-06 and was freshness-rechecked against the official Open Charge Alliance surface on 2026-10-02.

These records are `versioned`. Current legal/regulatory/technical claims still require separate current-source verification when a real task depends on them.

The GenAI/NIST candidate remains `HOLD_FRESHNESS_REVIEW`; EV promotion does not change that status.

## Historical governance evidence

A50.4 through A50.10B contain topology-bound evaluations from the pre-EV-promotion three-record world. Their scripts, packets, ledgers and tests remain in the repository as audit evidence, but active CI does not reinterpret those historical decisions against the new four-record topology.

Post-promotion canonical truth is owned by:

```text
uiux-factory/benchmarks/knowledge-canonical-state-v2.json
uiux-factory/core/benchmarks/knowledge_ev_canonical_apply.py
uiux-factory/scripts/validate_knowledge_ev_canonical_apply.py
```

## No vector database

Knowledge OS still uses no vector database or embeddings. Vector retrieval remains disabled until separately governed.

## Governance

Material decisions must continue to distinguish:

```text
reusable knowledge
vs project truth
vs inference/hypothesis
vs current evidence
vs human decision
```

Adding more records requires an explicit source, scope, non-duplication rationale, retrieval-value reason and bounded regression/rollback evidence. Corpus size is not a success metric.

Repository-owner standing delegation may continue bounded upgrade tasks only after required gates pass. It does not permit fabricated independent-human evidence, bypass failed checks or eliminate the final retrospective owner review after the broader `uiux-ai-workspace` upgrade is complete.
