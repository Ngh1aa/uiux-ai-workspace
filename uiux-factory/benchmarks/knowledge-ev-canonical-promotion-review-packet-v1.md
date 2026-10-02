# EV/OCPP Canonical Promotion — Governance Review Packet v1

Proposal: `knowledge-ev-canonical-promotion-proposal-v1`  
Candidate: `knowledge.domain.ev-charging-ocpp-transaction-semantics.v1`  
Review state: **PENDING**

## Decision requested

Choose exactly one verdict:

- `APPROVE_PROMOTION_TASK` — permits a separate explicit implementation task to prepare canonical files/index mutation under all listed controls.
- `REVISE_PROPOSAL` — proposal is directionally valid but controls/scope must change before approval.
- `HOLD` — do not proceed until a named dependency or freshness question is resolved.
- `REJECT` — do not promote this candidate under the current evidence/proposal.

Approval here never edits the canonical index and never enables auto-promotion.

## Evidence already earned

A50.8 human review:

- EV/OCPP knowledge condition preferred.
- no material regression.
- correctness and unsupported-claim-risk guards cleared.
- specificity/actionability and decision usefulness both strictly improved.
- derived verdict: `ACCEPT_FOR_INDEX_TRIAL`.

A50.9B controlled index trial:

- derived decision: `CANARY_PASS`.
- temporary topology: 3 canonical + EV draft = 4-record canary.
- EV retrieval isolated.
- Nova/Lumen/CENNEXT canonical retrieval unchanged before vs canary.
- EdTech/AI negative-domain isolation clear.
- context budget clear.
- rollback verified against exact canonical record set and exact `index.json` bytes/hash.
- GenAI/NIST freshness HOLD preserved.
- `promotion_proposal_allowed = true`.

## Proposed future canonical shape

Source draft:

```text
skills_UIUX/knowledge/drafts/records/ev-charging-ocpp-transaction-semantics.json
skills_UIUX/knowledge/drafts/content/ev-charging-ocpp-transaction-semantics.md
```

Proposed canonical namespace for a later implementation task:

```text
skills_UIUX/knowledge/records/ev-charging-ocpp-transaction-semantics.json
skills_UIUX/knowledge/content/ev-charging-ocpp-transaction-semantics.md
index ref: records/ev-charging-ocpp-transaction-semantics.json
```

The future canonical record must rewrite `content_ref` from the draft path to the canonical content path before indexing.

## Required reviewer checks

Before `APPROVE_PROMOTION_TASK`, confirm all three explicit review booleans as `true`:

1. **Source freshness rechecked** — OCPP 2.1 Edition 2 / Errata provenance still matches the candidate metadata at review time.
2. **Rollback plan accepted** — a future implementation can restore the exact pre-promotion canonical index and remove only the newly promoted canonical EV files if regression appears.
3. **Cross-domain risk accepted** — the A50.9B isolation/regression evidence is sufficient to justify a bounded promotion implementation task.

Also confirm that the candidate remains advisory-only and carries no evidence/gate/release authority.

## Non-negotiable future execution controls

A later promotion implementation task must:

- recheck current source/version freshness;
- validate the canonical copied `KnowledgeRecord` contract before index mutation;
- add exactly one canonical record/ref;
- keep vector search disabled;
- rerun EV retrieval isolation and Nova/Lumen/CENNEXT regression;
- rerun EdTech/AI negative-domain isolation;
- verify context budget;
- preserve GenAI/NIST HOLD unless separately governed;
- verify rollback after the canonical mutation plan;
- never infer product evidence from knowledge acceptance.

## Review entry

Update only `knowledge-ev-canonical-promotion-review-v1.json` with the independent human decision. Do not edit `skills_UIUX/knowledge/index.json` during governance review.
