# A50.7 — READY Candidate Draft & Validation

Status: **IMPLEMENTED / VERIFICATION PENDING**  
Date: **2026-10-02**  
Base: `main@438fdaeb0125a893691558bddd3de02cb4d15d53`

## Goal

Draft only the two A50.6 candidates that were explicitly marked `READY_FOR_CONTENT_DRAFT`, then validate their value and isolation without changing the canonical Knowledge OS index.

A50.7 is **not corpus acceptance**. A passing draft remains unindexed until a later explicit acceptance task.

## Inputs from A50.6

```text
EdTech / LTI  → READY_FOR_CONTENT_DRAFT
EV / OCPP     → READY_FOR_CONTENT_DRAFT
GenAI / NIST  → HOLD_FRESHNESS_REVIEW
```

The GenAI/NIST candidate stays on HOLD and receives no A50.7 draft record.

## Draft surfaces

```text
skills_UIUX/knowledge/drafts/records/edtech-lti-context-roles-services.json
skills_UIUX/knowledge/drafts/content/edtech-lti-context-roles-services.md

skills_UIUX/knowledge/drafts/records/ev-charging-ocpp-transaction-semantics.json
skills_UIUX/knowledge/drafts/content/ev-charging-ocpp-transaction-semantics.md
```

Both record files must parse through the existing `KnowledgeRecord` contract. They deliberately live under `knowledge/drafts/` and are not referenced by `skills_UIUX/knowledge/index.json`.

## Source verification

### EdTech / LTI

Primary source:

```text
https://www.1edtech.org/standards/lti
```

Verified 2026-10-02:

- 1EdTech identifies LTI 1.3 as the current version.
- LTI Advantage builds on LTI 1.3.
- Core service concepts include Assignment and Grade Services, Names and Role Provisioning Services and Deep Linking.

Draft ownership is limited to reusable platform/tool, context/role and service-boundary vocabulary. Education-site IA/admissions workflow and security implementation remain skill-owned.

### EV / OCPP

Primary source:

```text
https://openchargealliance.org/my-oca/ocpp/
```

Verified 2026-10-02:

- the OCA download surface lists OCPP 2.1 Edition 2;
- the current surface includes OCPP 2.1 Edition 2 Errata 2026-06;
- OCA describes OCPP 2.1 additions including ISO 15118-20 support, bidirectional charging/V2X, DER control, improved smart charging and extended transaction behavior.

Draft ownership is limited to reusable charging-system/protocol semantics. Generic state/error/progress methodology and engineering/certification procedure remain outside Knowledge OS.

## Why a shadow index

The canonical index remains exactly three records. To validate the two drafts using the real deterministic retriever, A50.7 creates an **ephemeral copied Knowledge OS tree** inside a temporary directory and writes a five-record `shadow-index.json` there:

```text
3 current canonical records
+ EdTech/LTI draft
+ EV/OCPP draft
= 5 shadow records
```

The source checkout is not modified by shadow-index construction.

This lets A50.7 test the real `KnowledgeIndex` + `KnowledgeRetriever` behavior while preserving the production/canonical boundary.

## Validation layers

Each READY draft must satisfy all of the following.

### 1. Proposal alignment

- draft candidate is still READY in A50.6;
- record id matches `proposed_record_id`;
- source URL and version match the proposal;
- draft domain matches the proposal;
- GenAI/NIST HOLD status remains unchanged.

### 2. Canonical non-mutation

- canonical index count remains `3`;
- canonical index contains no `drafts/` path;
- neither draft id exists in the canonical seed;
- exactly two draft record files exist in A50.7.

### 3. Knowledge-vs-skill duplication

A50.7 applies the existing substantive-line overlap approach against the related procedural skills. Exact substantive line duplication fails the draft proxy.

This is intentionally conservative: the draft may reference the same domain problem as a skill, but it must not copy the skill's workflow/methodology body.

### 4. Retrieval + domain isolation

For each draft, a query against the five-record shadow index must return only that draft.

Expected result:

```text
hits = [target draft]
domain_mismatch exclusions = 4
vector_search_used = false
```

This simultaneously checks retrieval fit and cross-domain noise isolation against all three existing records plus the other new draft.

### 5. Bounded usefulness proxy

The deterministic draft proxy reuses the A50.4 philosophy and checks:

```text
actionable_delta
proposal_alignment_clear
canonical_unindexed
domain_specificity
skill_duplication_clear
retrieval_noise_clear
provenance_clear
context_budget_clear
```

The only positive draft decision is:

```text
KEEP_DRAFT
```

`KEEP_DRAFT` means the draft is suitable for the next acceptance/evaluation phase. It does **not** mean KEEP as a canonical record, and it does not establish human/model usefulness.

## Human usefulness boundary

A50.7 explicitly keeps:

```text
human_usefulness_claim_allowed = false
human_usefulness_claimed = false
canonical_acceptance_allowed = false
index_mutation_allowed = false
vector_search_change_allowed = false
```

A deterministic shadow retrieval cannot prove that the additional knowledge improves model outputs for real EdTech or EV work. A later acceptance task must decide whether model-assisted/human usefulness evidence is required before index mutation.

## Executable surfaces

```text
benchmarks/knowledge-ready-candidate-drafts-v1.json
core/benchmarks/knowledge_ready_candidate_drafts.py
scripts/validate_knowledge_ready_candidate_drafts.py
tests/test_knowledge_ready_candidate_drafts_a50.py
```

Main UIUX Factory CI runs the A50.7 validator before the full pytest suite.

## Expected A50.7 result

```text
canonical index records = 3
draft records = 2
shadow index records = 5
KEEP_DRAFT = 2
REVISE_DRAFT = 0
GenAI/NIST = HOLD_FRESHNESS_REVIEW
canonical acceptance = false
index mutation = false
human usefulness claim = false
```

## Next gate

Only after A50.7 verification should a separate task consider **A50.8 — Candidate Acceptance Trial**.

A50.8 should decide, per candidate, whether to:

```text
ACCEPT_FOR_INDEX_TRIAL
REVISE_DRAFT
HOLD
REJECT
```

No candidate should be added to `skills_UIUX/knowledge/index.json` merely because A50.7 returns `KEEP_DRAFT`.
