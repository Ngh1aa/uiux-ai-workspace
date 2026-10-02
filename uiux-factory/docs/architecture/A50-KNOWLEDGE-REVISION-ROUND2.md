# A50.5R — Knowledge Revision Pass / Round 2

Status: **IMPLEMENTED — ROUND-TWO HUMAN REVIEW PENDING**  
Date: **2026-10-02**

## Why A50.5R exists

A50.5 round one produced a real human verdict of `REVISE_BEFORE_EXPANSION` rather than `CONSIDER_EXPANSION`.

The human review identified a specific pattern:

- Nova knowledge context improved locale/currency correctness but the baseline remained more immediately decision-useful in implementation details.
- Lumen knowledge context already improved both specificity/actionability and decision usefulness.
- CENNEXT knowledge context improved technical claim precision but the baseline remained stronger on buyer journey and proof presentation.

A50.5R therefore revises **only the two underperforming existing records**. It does not expand the corpus.

## Revision targets

### Nova / financial currency formatting

Preserved:

```text
numeric value + currency + locale/display context
locale-aware decimal/grouping rules
currency placement / negative forms
same-symbol ambiguity
presentation != accounting/exchange/tax policy
```

Added direct product application guidance:

```text
shared amount-formatting boundary
explicit locale fallback requirement
concrete QA matrix
cross-surface consistency checks
```

Canonical record remains:

```text
knowledge.domain.financial-currency-locale-formatting.v1
```

The source standard remains Unicode CLDR / UTS #35. The knowledge ID is not replaced because the domain fact model did not change; the curated application guidance was revised in place and `updated_at` was refreshed.

### CENNEXT / industrial motor claims

Preserved:

```text
component condition
motor/drive efficiency
load/system performance
repair/rewind quality
repair-versus-replace decision
traceable evidence basis
no automatic efficiency-gain claim
```

Added buyer-facing application guidance:

```text
intake → assessment → finding → options → approval → work → verification → return/follow-up
traceable proof modules
customer approval boundary
repair-versus-replace decision support
service claim != business outcome claim
```

Canonical record remains:

```text
knowledge.domain.industrial-motor-system-claims-doe.v1
```

The source basis remains U.S. DOE Motor Systems. A50.5R does not turn the record into engineering advice or a generic page-design workflow.

## Knowledge-vs-skill boundary

The revision remains inside Knowledge OS only because the added material is the **direct application implication of the domain reference**.

It does not own:

```text
full implementation workflow
full website information architecture
copywriting workflow
research process
release authority
engineering diagnosis
```

Those remain owned by routed skills, project truth and human authority.

## Round-two trial method

Round two is stored separately from round one:

```text
benchmarks/knowledge-value-trial-v2.json
benchmarks/knowledge-value-trial-mapping-v2.json
benchmarks/knowledge-value-human-reviews-v2.json
benchmarks/knowledge-value-review-packet-v2.md
```

Method:

1. Nova and CENNEXT keep the **round-one baseline outputs unchanged**.
2. Only their knowledge-assisted outputs are regenerated from the revised records.
3. Lumen is the unchanged control pair.
4. A/B labels are swapped/mixed relative to round one.
5. The same five-dimension human rubric and the same governance threshold remain unchanged.

This isolates the effect of the revision better than regenerating both sides.

## Blinding limitation

Round two remains **procedurally repository blind**, not cryptographically blind.

The original reviewer has seen round-one outputs, so same-reviewer carryover memory is a known limitation. The trial mitigates but cannot eliminate that limitation by:

- swapping A/B positions;
- keeping the condition mapping separate;
- keeping baseline text fixed for the two revised cases;
- preserving the old trial as immutable history.

No claim of independent randomized experimentation is made.

## Round-two governance

Before human review:

```text
human_review_complete = false
expansion_recommendation = HOLD_PENDING_HUMAN
expand_allowed = false
auto_mutation_allowed = false
```

A50.6 may be proposed only if the existing evaluator later derives `CONSIDER_EXPANSION`:

```text
material_regression_count = 0
baseline_preferred_count = 0
knowledge_preferred_count >= 2 of 3
knowledge condition strictly stronger on both:
  specificity_actionability
  decision_usefulness
in at least 2 of 3 cases
```

The threshold is intentionally unchanged from round one.

## Regression contract

CI must preserve all of the following:

- round-one review remains complete and derives `REVISE_BEFORE_EXPANSION`;
- round-two review remains pending until a new human review is committed;
- Nova and CENNEXT round-two baseline outputs exactly equal their round-one baseline outputs;
- Lumen remains the unchanged control pair;
- revised Nova output includes shared formatting boundary, explicit fallback and QA matrix;
- revised CENNEXT output includes buyer decision path, proof modules and approval boundary;
- A/B mapping remains mixed and does not overclaim cryptographic blinding;
- cross-version review ledgers cannot be mixed;
- knowledge still has no evidence/gate/release authority;
- corpus remains exactly three records.

## Next step

After this engineering PR is green and merged, perform the blind review using:

```text
uiux-factory/benchmarks/knowledge-value-review-packet-v2.md
```

Do not open `knowledge-value-trial-mapping-v2.json` before completing the scores, preference, rationale and material-regression judgment for all three cases.

If round two derives `CONSIDER_EXPANSION`, the next task may be **A50.6 — Corpus Expansion Proposal**. Otherwise, keep the corpus fixed and inspect the remaining knowledge/retrieval weakness instead of weakening the threshold.
