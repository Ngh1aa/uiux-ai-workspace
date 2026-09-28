# A12 — Benchmark & Regression Corpus

A12 turns Factory quality claims into a repeatable, versioned evaluation contract.

It does **not** claim that deterministic checks can replace a human Creative Director. Objective coverage and human aesthetic judgment are stored separately so the Factory cannot manufacture a design-quality verdict from machine evidence alone.

## Canonical surfaces

```text
uiux-factory/core/benchmarks/regression_corpus.py
uiux-factory/benchmarks/corpus/uiux-product-v1.json
uiux-factory/scripts/validate_benchmark_corpus.py
uiux-factory/tests/test_benchmark_corpus_a12.py
```

The existing `core/benchmarks/prompt_os_v1.py` remains a focused Prompt OS/profile benchmark. A12 adds the broader product-diversity corpus rather than replacing that benchmark.

## Corpus v1

The first canonical corpus contains eight materially different domains:

1. luxury commerce;
2. automotive/corporate;
3. B2B SaaS;
4. education;
5. public service;
6. editorial/media;
7. service business;
8. dashboard/application.

Each case preserves:

```text
brief
source truth categories
representative routes
required page roles
reference constraints
required hard evidence
human review status/rubric
screenshot pack status/viewports
tags
```

Every case receives a deterministic SHA-256 content hash. The corpus also receives a deterministic hash derived from its versioned case hashes. Reports from different corpus hashes cannot be compared as if they were the same evaluation set.

## Truthful human-review boundary

Fresh corpus cases intentionally start with:

```json
{
  "human_review": {
    "status": "pending",
    "verdict": null
  },
  "screenshot_pack": {
    "status": "pending"
  }
}
```

`pending` review is not a negative result; it means no human Creative Director verdict has been recorded yet.

The validator rejects a pending human review that already contains a verdict. A recorded review must reference a review artifact. The Factory must never fill this field merely because a model, heuristic or Vision Creative Director produced an advisory opinion.

## Objective result contract

A run may submit per-case objective evidence metadata:

```text
case_id
routes
page_roles
evidence_types
screenshot_viewports
hard_rule_failures
human_review_status
human_verdict (only when actually recorded)
```

The deterministic evaluator checks only whether the case's declared objective requirements are covered:

- every representative route is present;
- every required page role is represented;
- every required evidence class is present;
- required screenshot viewports are present;
- no hard-rule failure remains.

An objective pass with no human review becomes:

```text
objective_pass_pending_human
```

It is **not** converted into an aesthetic PASS.

## Complete reports

`build_benchmark_report()` records:

```text
corpus id/version/hash
run label
submitted/missing cases
objective pass count
human-reviewed count
per-case checks/status
```

A report is not complete unless all canonical cases are supplied.

## Regression comparison

`compare_benchmark_reports()` compares only reports from the exact same corpus hash and emits case-level changes:

```text
unchanged
objective_recovery
objective_regression
```

The comparator deliberately does **not** produce:

- an overall aesthetic score;
- a provider/model winner;
- a human-quality ranking;
- a fabricated Creative Director verdict.

A later benchmark experiment may attach real human review artifacts and analyze them, but that is a separate evidence channel.

## CI

`UIUX Factory CI` executes:

```bash
python scripts/validate_benchmark_corpus.py
```

alongside Flow/runtime validation. The test suite additionally locks hashing, eight-domain diversity, pending-review truthfulness, objective evidence failure behavior, complete-report semantics and same-corpus comparison.

## Expansion rule

A future corpus version may add cases or recorded screenshot/human-review artifacts, but changing a case changes its hash. If evaluation requirements materially change, bump the corpus version rather than silently rewriting historical comparisons.
