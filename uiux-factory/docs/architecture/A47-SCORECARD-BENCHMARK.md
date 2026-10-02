# A47.2 — Brain Scorecard Regression Benchmark

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A47.1 Provenance-Aware Brain Scorecard

## 1. Purpose

A47.2 locks the scorecard truth boundary with a deterministic read-only corpus.

Canonical surfaces:

```text
benchmarks/scorecard-v1.json
core/benchmarks/scorecard_regression.py
scripts/validate_scorecard_benchmark.py
tests/test_scorecard_benchmark_a47.py
```

The benchmark does not participate in product/runtime evaluation. It only checks that A47.1 keeps existing source channels truthful and separate.

## 2. Corpus coverage

The v1 corpus covers:

- `insufficient_evidence` with zero critic findings;
- `passed` with a P0 advisory critic finding;
- `failed` with mixed P1/P2 findings;
- `blocked` with an integrity warning / incomplete lineage;
- `passed` with an integrity ERROR;
- duplicate provenance source refs that must be rejected.

The intentionally counter-intuitive `passed + integrity ERROR` case is important: the scorecard must not silently rewrite the canonical `RunEvaluation.outcome`. The integrity error remains visible in its own channel so downstream human/runtime policy can decide what it means.

## 3. Locked invariants

Every non-rejected case asserts:

```text
scorecard.runtime_outcome == corpus.expected_runtime_outcome
```

and also verifies:

```text
critic P0 count is preserved
integrity_valid is preserved
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

The provenance-collision case must fail closed.

## 4. Read-only guard

Tests hash:

```text
core/brain_os/scorecard.py
```

before and after benchmark evaluation and require byte-identical content.

The benchmark evaluator does not import/call runtime/gate/release execution owners such as:

```text
RunEvaluator.evaluate(...)
effective_evidence(...)
gate_evidence_errors(...)
ProviderManagedRunner
ManagedFlowController
ProductionReleaseController
run_target_command
release_action
merge_pull_request
```

## 5. CI integration

Main `UIUX Factory CI` runs:

```text
python scripts/validate_scorecard_benchmark.py
```

with the other benchmark validators before the full pytest suite.

## 6. Acceptance criteria

A47.2 is complete when:

- [x] all canonical runtime outcome classes are represented;
- [x] advisory critic severity can coexist with canonical runtime PASS without changing it;
- [x] integrity WARNING/ERROR states remain separate scorecard channels;
- [x] `insufficient_evidence` cannot be upgraded by zero critic findings;
- [x] duplicate source provenance is rejected;
- [x] benchmark evaluation is read-only against production scorecard code;
- [x] CI invokes the deterministic benchmark validator;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 7. Handoff

After A47.2 is green and merged, re-audit architecture truth before defining A48. The remaining high-level debts are expected to be provider/lifecycle convergence and documentation truth reconciliation; neither should be changed without first checking current source owners and guardrails.
