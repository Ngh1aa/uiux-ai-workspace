# A50.10B — EV Canonical Promotion Shadow Implementation

Status: **SHADOW APPLY / REPOSITORY CANONICAL STATE UNCHANGED**  
Date: **2026-10-02**

## Purpose

Execute the exact EV/OCPP canonical-promotion shape in an isolated workspace before changing the repository canonical index.

A50.10A established the proposal and governance boundary. The repository owner then recorded standing delegation allowing follow-up implementation tasks to continue only when all required evidence and CI gates pass. That delegation is kept separate from the still-truthful independent-human review ledger; this phase does not fabricate independent-human evidence.

## Source freshness

The official Open Charge Alliance download surface was rechecked on 2026-10-02 and still exposed:

```text
OCPP 2.1 Edition 2
OCPP 2.1 Edition 2 Errata 2026-06
```

This matches candidate version:

```text
OCPP-2.1-Edition-2-Errata-2026-06
```

## Shadow apply

The evaluator copies the current `skills_UIUX/knowledge` tree into a temporary workspace and then performs the future canonical mutation there:

1. copy the EV draft content to `skills_UIUX/knowledge/content/ev-charging-ocpp-transaction-semantics.md`;
2. copy the EV record to `skills_UIUX/knowledge/records/ev-charging-ocpp-transaction-semantics.json`;
3. rewrite `content_ref` from the draft namespace to the canonical content path;
4. validate the copied `KnowledgeRecord` contract;
5. append exactly one canonical index ref;
6. load the real `KnowledgeIndex`/`KnowledgeRetriever` against the 4-record shadow topology;
7. verify EV retrieval isolation;
8. verify Nova/Lumen/CENNEXT retrieval regression remains clear;
9. verify EdTech/AI negative-domain isolation;
10. verify context budget and vector-search-disabled state;
11. roll the shadow workspace back to the exact 3-record baseline and remove only the shadow EV canonical assets.

The real repository index is read before/after and must remain byte-identical.

## Decision

A pass returns:

```text
READY_FOR_CANONICAL_APPLY
```

That means only that A50.10C may perform the repository mutation after migrating pre-promotion CI invariants.

A50.10B itself keeps:

```text
repository_index_mutation_allowed = false
repository_canonical_assets_commit_allowed = false
auto_promotion_in_this_phase = false
vector_search_change_allowed = false
product_evidence = false
```

## Required migration before repository apply

The following historical validators encode a three-record pre-promotion world and must not be executed unchanged after EV becomes canonical:

- `validate_knowledge_ev_controlled_index_trial.py`
- `validate_knowledge_edtech_controlled_index_trial.py`
- `validate_knowledge_ev_canonical_promotion_proposal.py`

A50.10C must preserve these artifacts as historical evidence while moving active CI to post-promotion invariants. The final owner retrospective review remains deferred until the broader `uiux-ai-workspace` upgrade is complete.
