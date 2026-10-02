# A50.3 — Curated Seed Knowledge + Real-Project Retrieval Dogfood

Status: **IMPLEMENTED ON FEATURE BRANCH**  
Date: **2026-10-02**

## Goal

A50.3 moves Knowledge OS from an empty canonical index to a deliberately tiny, traceable seed corpus and verifies that deterministic retrieval is useful on materially different project profiles without becoming a duplicate skill library.

The success condition is precision, not corpus size.

## Seed policy

Only three records are admitted in v1:

| Record | Domain | Primary source | Intended project dogfood |
| --- | --- | --- | --- |
| financial currency/locale formatting | `financial-services` | Unicode CLDR / UTS #35 Part 3 | Nova |
| cultural-object metadata/rights | `art-culture` | IIIF Presentation API 3.0 | Lumen |
| industrial motor-system claims | `industrial-services` | U.S. DOE Motor Systems | CENNEXT |

The sources are public standards/authoritative domain references. The repository stores concise paraphrased reference material, not copied articles or long source passages.

## Why these records qualify as knowledge

They encode reusable domain/reference facts:

- locale/currency presentation varies by locale and currency data;
- cultural-object metadata, attribution/required statements, rights and provider identity are distinct presentation concepts in IIIF;
- DOE motor resources distinguish motor/system efficiency and provide repair-specific technical references, so repair and performance claims should not be collapsed into one unsupported promise.

They do **not** define design workflow, critique procedure, acceptance criteria, routing rules or release gates.

## Duplication boundary

A50.3 audits the active skill corpus before seeding.

Examples of methodology that remains owned by skills and is therefore excluded from Knowledge OS:

```text
financial workflow/state/evidence method
    → financial-product-intelligence/SKILL.md

asset choice / crop / responsive art direction method
    → asset-media-and-art-direction/SKILL.md

accessibility workflow and release checks
    → accessibility/SKILL.md
```

Seed content is regression-guarded against common methodology headings such as `Workflow`, `Acceptance criteria` and numbered procedural steps. No `SKILL.md` may exist under `skills_UIUX/knowledge/`.

## Canonical seed index

`skills_UIUX/knowledge/index.json` now contains exactly three metadata records.

A50.3 treats the count as a deliberate governance limit for this phase. Adding record four is not forbidden forever, but it must be an explicit later change with source, scope and retrieval-value rationale.

## Project retrieval dogfood

Benchmark:

```text
benchmarks/knowledge-project-dogfood-v1.json
core/benchmarks/knowledge_project_dogfood.py
scripts/validate_knowledge_project_dogfood.py
```

Profiles:

### Nova

```text
repository = https://github.com/Ngh1aa/Nova
domain = financial-services
stage = implementation
terms = currency / amount / money / multi-currency
expected = financial currency/locale record only
```

### Lumen

```text
repository = https://github.com/Ngh1aa/Lumen
domain = art-culture
stage = research
terms = museum / metadata / rights / artwork
expected = IIIF cultural-object record only
```

### CENNEXT

```text
repository = https://github.com/Ngh1aa/cennext-b2b-prototype
domain = industrial-services
stage = research
terms = motor / repair / efficiency / technical claims
expected = DOE motor-system record only
```

For every case, the other two records must be excluded specifically by `domain_mismatch`. A dogfood PASS therefore proves cross-domain isolation as well as expected retrieval.

## Truth boundary

Dogfood scope is explicitly:

```text
curated_retrieval_profile_dogfood_not_product_or_user_validation_evidence
```

It does not prove:

- the external source is sufficient for a specific product decision;
- the source is current beyond its version/provenance metadata;
- users understand the resulting interface;
- the project has implemented the knowledge correctly;
- the product outcome improved.

Knowledge remains advisory context and cannot satisfy runtime gates or release authority.

## Source freshness

The CLDR record is pinned to the stable 48.2 specification. The IIIF record is pinned to Presentation API 3.0. The DOE record is curated against the Motor Systems resource page on 2026-10-02.

These are `versioned`, not `time_sensitive`, because the record refers to a named source/version/reference surface. If a later product task depends on current legal/regulatory/technical requirements, it must obtain current external evidence separately.

## Regression guards

A50.3 adds checks for:

- exactly three canonical seed records;
- exact source host set: Unicode, IIIF, U.S. DOE;
- one explicit domain per seed record;
- no evidence/gate/release authority;
- no `SKILL.md` in Knowledge OS;
- no procedural skill-section structure in seed content;
- exact one-record retrieval for Nova/Lumen/CENNEXT;
- two cross-domain exclusions per dogfood case.

## Completion criteria

A50.3 is complete when:

```text
3-source seed corpus is canonical
all content has traceable primary/authoritative sources
duplication guards pass
Nova retrieves only financial record
Lumen retrieves only cultural record
CENNEXT retrieves only industrial record
Main CI runs project retrieval dogfood
full Factory regression remains green
A13/A20 dogfood remains green when path-triggered
```

## Next task

**A50.4 — Knowledge Usefulness Evaluation + Corpus Governance.**

Compare representative reasoning/context with vs without seed knowledge, measure actionability and duplication/noise, and define KEEP / REVISE / REMOVE / EXPAND decisions before adding broader knowledge categories. Vector search remains deferred.
