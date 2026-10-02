# A50.9A — EdTech Draft Revision + Blind Acceptance Retry

Status: **IMPLEMENTED / HUMAN REVIEW PENDING**  
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

A50.9A creates a new single-case blind A/B trial:

```text
benchmarks/knowledge-edtech-revision-trial-v1.json
benchmarks/knowledge-edtech-revision-mapping-v1.json
benchmarks/knowledge-edtech-revision-human-review-v1.json
benchmarks/knowledge-edtech-revision-review-packet-v1.md
```

The A50.8 baseline is held fixed exactly. Only the knowledge-assisted condition changes, so the trial measures the revision rather than a moving baseline.

The mapping stays separate from the review packet. Human review remains required before unblinding.

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

Pending review derives `HOLD`.

## Engineering guards

The evaluator also requires:

- merged A50.8 EdTech verdict is still `REVISE_DRAFT`;
- A50.8 baseline is preserved exactly;
- v1 EdTech draft/history remains present;
- v2 draft validates as `KnowledgeRecord`;
- v2 record is not in canonical index;
- shadow retrieval returns only the v2 EdTech record for the EdTech query;
- canonical index remains exactly three records;
- required concrete state/recovery concepts exist in the v2 content;
- vector search remains unused.

## Authority boundary

A50.9A never enables:

```text
index_mutation_allowed = false
canonical_acceptance_allowed = false
auto_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false
```

Even a later `ACCEPT_FOR_INDEX_TRIAL` result only permits a controlled index-trial task. It does not promote the EdTech record into the canonical index.

## Next step

After engineering verification, an independent human reviews:

```text
benchmarks/knowledge-edtech-revision-review-packet-v1.md
```

Do not open the mapping until scoring is complete.
