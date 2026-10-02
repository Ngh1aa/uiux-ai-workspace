# A50.5R — Knowledge Revision Pass / Round 2

Status: **COMPLETE — ROUND-TWO HUMAN REVIEW DERIVED `CONSIDER_EXPANSION`**  
Date: **2026-10-02**

## Why A50.5R exists

A50.5 round one produced a real human verdict of `REVISE_BEFORE_EXPANSION` rather than `CONSIDER_EXPANSION`.

The human review identified a specific pattern:

- Nova knowledge context improved locale/currency correctness but the baseline remained more immediately decision-useful in implementation details.
- Lumen knowledge context already improved both specificity/actionability and decision usefulness.
- CENNEXT knowledge context improved technical claim precision but the baseline remained stronger on buyer journey and proof presentation.

A50.5R therefore revised **only the two underperforming existing records**. It did not expand the corpus.

## Revision targets

### Nova / financial currency formatting

Preserved:

```text
numeric value + currency + locale/display context
locale-aware decimal/grouping rules
currency placement / negative forms
same-symbol ambiguity
multi-currency presentation context
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

The source standard remains Unicode CLDR / UTS #35. The knowledge ID was not replaced because the domain fact model did not change; the curated application guidance was revised in place.

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
2. Only their knowledge-assisted outputs change.
3. Lumen is the unchanged control pair.
4. A/B labels are swapped/mixed relative to round one.
5. The same five-dimension human rubric and the same governance threshold remain unchanged.

This isolates the effect of the revision better than regenerating both sides.

## Blinding limitation

Round two remains **procedurally repository blind**, not cryptographically blind.

The reviewer had seen round-one outputs, so same-reviewer carryover memory is a known limitation. The trial mitigates but cannot eliminate that limitation by:

- swapping A/B positions;
- keeping the condition mapping separate;
- keeping baseline text fixed for the two revised cases;
- preserving the old trial as immutable history.

No claim of independent randomized experimentation is made.

## Round-two human result

The reviewer completed all three blind-first judgments before opening the v2 mapping.

After unblinding:

```text
Nova     knowledge condition = A
Lumen    knowledge condition = B
CENNEXT  knowledge condition = A
```

Recorded preferences:

```text
Nova     → A / knowledge preferred
Lumen    → B / knowledge preferred
CENNEXT  → A / knowledge preferred
```

Derived counts:

```text
human_review_complete = true
reviewed_case_count = 3
knowledge_preferred_count = 3
baseline_preferred_count = 0
tie_count = 0
insufficient_count = 0
material_regression_count = 0
joint_usefulness_win_count = 3
```

The unchanged evaluator therefore derives:

```text
CONSIDER_EXPANSION
```

The threshold was not changed to fit the result.

## Governance boundary

`CONSIDER_EXPANSION` is **not** permission to mutate the corpus automatically.

The canonical evaluator still returns:

```text
expand_allowed = false
auto_mutation_allowed = false
current_run_evidence = false
product_evidence = false
```

A50.5R establishes enough governance evidence to open an **A50.6 Corpus Expansion Proposal**, not to add records directly.

A50.6 must still perform source/ownership/duplication/scope review for every proposed record or category before any canonical index change.

## Regression contract

CI must preserve all of the following:

- round-one review remains complete and derives `REVISE_BEFORE_EXPANSION`;
- round-two review remains complete and derives `CONSIDER_EXPANSION`;
- round-two human preferences remain 3/3 knowledge, 0 baseline, 0 ties;
- round-two joint specificity/actionability + decision-usefulness wins remain 3/3;
- material regressions remain zero;
- Nova and CENNEXT round-two baseline outputs exactly equal their round-one baseline outputs;
- Lumen remains the unchanged control pair;
- revised Nova output includes shared formatting boundary, explicit fallback and QA matrix;
- revised CENNEXT output includes buyer decision path, proof modules and approval boundary;
- A/B mapping remains mixed and does not overclaim cryptographic blinding;
- cross-version review ledgers cannot be mixed;
- knowledge still has no evidence/gate/release authority;
- corpus remains exactly three records until an explicit A50.6 change is separately accepted.

## Next step

Open **A50.6 — Corpus Expansion Proposal** as a governance/design task only.

A50.6 may propose candidate domains/records, but must not mutate `skills_UIUX/knowledge/index.json` unless each candidate passes explicit source, ownership, duplication, freshness, scope and retrieval-value review in a later accepted implementation step.

Vector search remains deferred until corpus breadth and deterministic retrieval justify it.
