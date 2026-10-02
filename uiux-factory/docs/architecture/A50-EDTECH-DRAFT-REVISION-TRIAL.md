# A50.9A — EdTech Draft Revision + Blind Acceptance Retry

Status: **VERIFIED / HUMAN REVIEW COMPLETE / ACCEPT_FOR_INDEX_TRIAL**  
Date: **2026-10-02**

## Trigger

A50.8 completed blind human review with:

```text
EdTech / LTI → REVISE_DRAFT
EV / OCPP    → ACCEPT_FOR_INDEX_TRIAL
```

EdTech failed only the strict joint-usefulness guard: the knowledge-assisted output was preferred and more specific, but `decision_usefulness` remained tied with baseline (`1 == 1`).

## Revision strategy

A50.9A does not overwrite the A50.7/A50.8 EdTech v1 draft. Historical evidence remains intact.

It adds a versioned v2 draft:

```text
knowledge.domain.edtech-lti-context-roles-services.v2
```

The revision keeps LTI 1.3 / LTI Advantage service truth but adds concrete state and recovery boundaries for:

```text
launch
NRPS roster/context access
Deep Linking content selection
AGS grade exchange
```

The revised content adds:

- explicit state names;
- source-of-truth requirements for visible states;
- distinctions among not configured / role-limited / failed / unknown;
- context-preserving recovery guidance;
- retry/resubmit only when the implementation safely supports it;
- explicit protection against inferring AGS/NRPS/Deep Linking support from LTI 1.3 alone.

This remains domain/reference knowledge. Generic error/retry methodology still belongs to routed UX skills.

## Blind retry

A50.9A uses a single-case blind A/B trial:

```text
benchmarks/knowledge-edtech-revision-trial-v1.json
benchmarks/knowledge-edtech-revision-mapping-v1.json
benchmarks/knowledge-edtech-revision-human-review-v1.json
benchmarks/knowledge-edtech-revision-review-packet-v1.md
```

The A50.8 baseline was held fixed exactly. Only the knowledge-assisted condition changed, so the trial measured the revision rather than a moving baseline.

The mapping remained separate from the review packet until scoring was complete.

## Human review result

The independent blind-first review completed with:

```text
Preferred output: B
Material regression: false

A:
correctness = 1
specificity_actionability = 1
relevance_noise = 2
unsupported_claim_risk = 2
decision_usefulness = 1

B:
correctness = 2
specificity_actionability = 2
relevance_noise = 2
unsupported_claim_risk = 2
decision_usefulness = 2
```

After scoring, the mapping was opened:

```text
knowledge condition = B
baseline condition = A
```

The human rationale identified the main improvement as decision-useful specificity rather than terminology density: the knowledge condition names NRPS, Deep Linking and AGS, makes explicit that a successful launch proves only the launch path, gives concrete service states only when project truth can distinguish them, ties visible state to an authoritative observation, and separates configuration/role limitations from temporary failure and unknown states.

The review also recorded two remaining caveats that do not rise to material regression:

- the revised output does not explicitly name a generic `empty state`;
- it does not identify role initiators as explicitly as the older A50.8 packet.

Those gaps remain useful future-hardening inputs but do not invalidate this revision trial.

## Deep Linking cancellation verification

A50.9A separately checked the reviewer's uncertainty around the product-level state:

```text
content_selection_cancelled
```

The current 1EdTech Deep Linking specification supports the underlying distinction: a user/platform workflow may be cancelled before resource-link creation, and a Deep Linking Response may contain no selected/created items.

However, the LTI protocol does not define a literal protocol status named `cancelled`.

Therefore the A50.9A interpretation remains:

```text
content_selection_cancelled = product-level derived state
```

It is valid only when project/implementation truth can actually distinguish cancellation from no selection, error, or another return path. The record must not present it as a normative LTI protocol status.

## Acceptance policy

Allowed verdicts remain:

```text
ACCEPT_FOR_INDEX_TRIAL
REVISE_DRAFT
HOLD
REJECT
```

`ACCEPT_FOR_INDEX_TRIAL` requires all of:

```text
knowledge preferred
material_regression = false
knowledge correctness >= baseline
knowledge unsupported_claim_risk >= baseline
knowledge specificity_actionability > baseline
knowledge decision_usefulness > baseline
```

The completed review satisfies every guard, so the unchanged evaluator derives:

```text
ACCEPT_FOR_INDEX_TRIAL
```

## Engineering guards

The evaluator also verifies:

- merged A50.8 EdTech verdict remains `REVISE_DRAFT`;
- A50.8 baseline is preserved exactly;
- v1 EdTech draft/history remains present;
- v2 draft validates as `KnowledgeRecord`;
- v2 record is not in canonical index;
- shadow retrieval returns only the v2 EdTech record for the EdTech query;
- canonical index remains exactly three records;
- required concrete state/recovery concepts exist in the v2 content;
- vector search remains unused.

Canonical-state tests now assert the completed human result while retaining separate fixture coverage for:

```text
PENDING → HOLD
baseline preferred → REVISE_DRAFT
material regression → REJECT
strict joint usefulness win → ACCEPT_FOR_INDEX_TRIAL
```

## Authority boundary

A50.9A still never enables:

```text
index_mutation_allowed = false
canonical_acceptance_allowed = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

`ACCEPT_FOR_INDEX_TRIAL` permits only a separate controlled index-trial task. It does not promote the EdTech record into the canonical index.

## Next step

EdTech may now enter a controlled index trial equivalent in rigor to the EV A50.9B canary:

- temporary/shadow index only;
- canonical retrieval regression;
- cross-domain isolation;
- context-budget check;
- rollback verification;
- explicit no-auto-promotion boundary.

Canonical `skills_UIUX/knowledge/index.json` remains unchanged until a later explicit promotion/governance decision.
