# A50.10C — EV Canonical Apply

Status: **CANONICAL APPLY UNDER CI / FINAL OWNER REVIEW DEFERRED**  
Date: **2026-10-02**

## Purpose

Promote the verified EV/OCPP knowledge candidate from the draft namespace into the canonical Knowledge OS after A50.9B `CANARY_PASS`, A50.10A bounded promotion proposal/governance, and A50.10B `READY_FOR_CANONICAL_APPLY` shadow execution.

This phase is the first phase allowed to change the repository canonical topology.

## Canonical mutation

A50.10C adds exactly one canonical record/content pair:

```text
skills_UIUX/knowledge/records/ev-charging-ocpp-transaction-semantics.json
skills_UIUX/knowledge/content/ev-charging-ocpp-transaction-semantics.md
```

and appends exactly one index ref:

```text
records/ev-charging-ocpp-transaction-semantics.json
```

The canonical corpus therefore moves from three to four records. The EV canonical content is byte-identical to the accepted draft content; the record is semantically identical to the draft record except that `content_ref` points to the canonical content namespace.

## Active post-promotion truth

`knowledge-canonical-state-v2.json` is the explicit post-promotion state contract. Its evaluator verifies:

- exact four-record index refs and IDs;
- one domain per canonical record;
- EV canonical record/content provenance and semantic-copy integrity;
- advisory-only and no-authority/evidence/gate/release boundaries;
- Nova, Lumen, CENNEXT and EV retrieval isolation;
- EdTech and AI-software negative-domain isolation;
- context budget and vector-search-disabled state;
- GenAI/NIST `HOLD_FRESHNESS_REVIEW` preservation;
- repository-owner standing delegation and deferred final owner review;
- historical-test freeze and active-CI migration;
- an exact rollback contract.

Pass decision:

```text
CANONICAL_APPLY_PASS
```

## Historical invariant migration

A50.4 through A50.10B contain valid historical evidence gathered while canonical topology had exactly three records and EV remained unindexed. Re-running those topology-bound evaluators after promotion would turn correct historical assertions into false current-state requirements.

A50.10C therefore preserves their files but freezes their topology-bound test modules after the EV canonical ref appears. Active CI no longer directly invokes those historical validators.

This is not a coverage reduction: active topology coverage moves to the A50.10C canonical-state validator while generic architecture/retrieval tests continue to run and are migrated to the four-record truth.

## Rollback

If the canonical apply introduces a regression, rollback is constrained to:

1. restore `skills_UIUX/knowledge/index.json` to the previous exact three refs;
2. remove only the new canonical EV record;
3. remove only the new canonical EV content;
4. preserve EV draft/revision/governance evidence;
5. preserve owner-delegation and review history.

## Boundaries preserved

```text
vector_search_change_allowed = false
product_evidence = false
GenAI/NIST = HOLD_FRESHNESS_REVIEW
final owner retrospective review = DEFERRED_UNTIL_UPGRADE_COMPLETE
```

The repository-owner standing delegation authorizes bounded continuation after passing gates; it does not transform AI/model work into independent-human evidence and does not permit failed checks to be bypassed.
