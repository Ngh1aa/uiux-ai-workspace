# A50.13 — EdTech/LTI Canonical Apply

Status: **CANONICAL APPLY CANDIDATE / FIVE-RECORD TRUTH GATED BY CI**  
Date: **2026-10-02**

## Purpose

Apply the separately authorized EdTech/LTI v2 promotion only after A50.11 governance approval and A50.12 shadow rehearsal both passed.

The target canonical topology is exactly five records:

```text
financial-services
art-culture
industrial-services
mobility-ev
education-edtech
```

## Promotion

A50.13 adds exactly one canonical ref:

```text
records/edtech-lti-context-roles-services-v2.json
```

and exactly two canonical assets:

```text
skills_UIUX/knowledge/records/edtech-lti-context-roles-services-v2.json
skills_UIUX/knowledge/content/edtech-lti-context-roles-services-v2.md
```

The canonical content is an exact copy of the accepted revision content. The canonical record is a semantic copy of the revision record with only `content_ref` rewritten to the canonical content path.

## Source freshness

The source basis remains official 1EdTech LTI:

```text
LTI core = LTI 1.3
LTI Advantage = AGS 2.0 + NRPS 2.0 + Deep Linking 2.0
```

The canonical record remains versioned, advisory-only and non-evidence.

## Post-promotion executable truth

Current truth is defined by:

```text
benchmarks/knowledge-canonical-state-v3.json
core/benchmarks/knowledge_edtech_canonical_apply.py
scripts/validate_knowledge_edtech_canonical_apply.py
```

The validator requires:

- exact five-record topology;
- unique record/domain identities;
- EdTech canonical record/content integrity against the accepted revision;
- source-freshness metadata match;
- advisory/no-authority boundary;
- financial/art/industrial/EV/EdTech retrieval regression clear;
- AI negative-domain isolation;
- bounded context delivery;
- vector search disabled;
- GenAI/NIST `HOLD_FRESHNESS_REVIEW` preserved;
- standing owner delegation intact;
- topology-bound proposal/shadow tests frozen as historical evidence;
- proposal/shadow validators removed from active CI;
- A50.13 validator active;
- exact rollback contract preserved;
- final owner review still deferred.

The only passing decision is:

```text
CANONICAL_APPLY_PASS
```

## Rollback

If the canonical apply regresses, rollback must restore the exact pre-EdTech four-record index:

```text
records/financial-currency-locale-formatting.json
records/cultural-object-metadata-rights-iiif.json
records/industrial-motor-system-claims-doe.json
records/ev-charging-ocpp-transaction-semantics.json
```

and remove only:

```text
skills_UIUX/knowledge/records/edtech-lti-context-roles-services-v2.json
skills_UIUX/knowledge/content/edtech-lti-context-roles-services-v2.md
```

Revision history, governance history and the EV canonical record remain preserved.

## Authority boundary

Canonical acceptance still does not make retrieved knowledge current-run evidence and does not grant gate/release authority:

```text
advisory_only = true
current_run_evidence = false
vector_search_used = false
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
product_evidence = false
```

GenAI/NIST remains freshness-held and is not promoted by this phase. Final retrospective owner review remains deferred until the broader `uiux-ai-workspace` upgrade is complete.
