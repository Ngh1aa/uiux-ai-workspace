# A45.3 — Repair Proposal Benchmark / Policy Guard

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A45.1 Repair Proposal Orchestrator + A45.2 Repair Lineage Graph Adapter

## Purpose

A45.3 adds a deterministic, read-only regression benchmark that locks the intended critique → repair-proposal policy without participating in production execution.

Canonical artifacts:

```text
benchmarks/repair-proposals-v1.json
core/benchmarks/repair_proposal_regression.py
scripts/validate_repair_proposal_benchmark.py
tests/test_repair_proposal_benchmark_a45.py
```

The main UIUX Factory CI runs the validator alongside the existing product and routing benchmarks.

## Coverage

The corpus covers:

- visual
- UX / IA
- design system
- accessibility
- product
- runtime
- evidence / truth
- unknown/custom critic fallback
- P0 / P1 / P2 severity behavior

For each case it asserts:

```text
critic → target stage
critic → retest evidence types
P0 → requires_human_approval=true
RootCause.status = PROPOSED
RepairDirective.status = PROPOSED
RetestRequirement.status = PENDING
RetestRequirement.evidence_refs = []
```

It also asserts the A45.2 graph shape remains exactly:

```text
CAUSED_BY
REPAIRED_BY
REQUIRES_RETEST
```

## False-verification guard

Every benchmark case must prove that proposal creation does not produce:

```text
VERIFIED_BY
RETESTED_BY
canonical trusted flags
execution claims
verification claims
acceptance/resolution/gate/evidence effects
```

The benchmark therefore fails if future code accidentally turns proposal planning into execution or truth authority.

## Read-only guarantee

Tests hash the production proposal sources before and after a full benchmark run:

```text
core/brain_os/repair_orchestrator.py
core/brain_os/adapters/repair_lineage.py
```

The hashes must remain byte-identical.

The benchmark evaluator itself is statically guarded against importing/calling runtime execution, gate or release owners.

## CI behavior

`.github/workflows/uiux-factory-ci.yml` now runs:

```text
python scripts/validate_benchmark_corpus.py
python scripts/validate_routing_benchmark.py
python scripts/validate_repair_proposal_benchmark.py
python -m pytest -q tests
```

A benchmark mismatch fails the foundation lane before merge.

## Acceptance criteria

- [x] deterministic corpus covers all current critic families plus fallback;
- [x] all severity levels are represented;
- [x] target-stage mapping is regression-tested;
- [x] retest evidence mapping is regression-tested;
- [x] P0 human-approval requirement is regression-tested;
- [x] proposal statuses remain PROPOSED/PENDING;
- [x] false `VERIFIED_BY` / `RETESTED_BY` relations are prohibited;
- [x] trusted flags and execution/verification claims are prohibited;
- [x] benchmark is read-only against production proposal sources;
- [x] main CI executes the benchmark validator;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## Handoff

A45 completes the advisory critique → repair-proposal → relationship-graph loop while deliberately stopping before execution. The next roadmap step should be chosen from the repo's architecture truth after A45.3 merges; do not introduce repair execution unless a separate authority/evidence contract explicitly owns it.
