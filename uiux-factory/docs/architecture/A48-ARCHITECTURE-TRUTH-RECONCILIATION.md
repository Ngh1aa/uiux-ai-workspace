# A48.1 — Post-A47 Architecture Truth Reconciliation

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Baseline: `main@38b11b347281cba8f8dd0b3cd6f99dcba62fdb95`

## 1. Why A48.1 exists

A41–A47 materially changed Brain OS capability, but the architecture index and A40-era runtime map still described several merged capabilities as future or unimplemented.

That documentation drift is itself an architecture risk: later tasks may accidentally create duplicate systems because the source-of-truth map says an existing capability does not exist.

A48.1 reconciles documentation with current source/tests before any deeper provider/lifecycle convergence work.

## 2. Reconciled capabilities

The current map now records these as implemented bounded capabilities:

```text
A41 — Brain core + critique/repair contracts
A42 — EvidenceGraph + integrity / lineage adapters
A43 — canonical flow selection + JIT context + routing benchmark
A44 — multi-discipline advisory critics
A45 — proposal-only repair synthesis + graph projection + benchmark
A46 — typed project-scoped semantic memory + post-routing recall + benchmark
A47 — provenance-aware Brain scorecard + benchmark
```

None of these changes the canonical Flow OS executable owner.

## 3. Canonical owners preserved

A48.1 explicitly preserves:

```text
core/runtime/flow_os/                    → shared executable Flow OS
skills_UIUX/                             → declarative skills / flows / policy
core/evaluation/run_evaluator.py         → canonical terminal runtime outcome
core/runtime/flow_os/evidence.py         → managed runtime evidence truth
core/provenance/                         → provenance / release evidence
uiux-factory/qa/                         → rendered/runtime QA truth
```

Brain OS remains a bounded reasoning/control and aggregation layer above these owners.

## 4. Resolved stale claims

The old runtime map incorrectly still claimed that:

- Brain OS reasoning/control was not implemented;
- typed design rationale / hypothesis / decision memory was future only;
- unified multi-discipline critique / repair synthesis did not exist;
- a provenance-aware Brain scorecard did not exist.

Those statements are removed/replaced with source-backed current ownership.

## 5. Remaining true debt

A48.1 deliberately does **not** pretend all architecture convergence is complete.

Two active execution/convergence concerns remain:

1. Factory internal provider lane:

```text
core/runtime/free_provider.py
```

and managed provider-neutral lane:

```text
core/runtime/flow_os/provider*.py
```

use different provider entry/capability shapes.

2. Factory product lifecycle:

```text
run.py + core/manager/
```

and managed CLI lifecycle:

```text
skills_UIUX/scripts/uiux-agent.py + ManagedFlowController
```

share canonical routing/runtime owners but do not expose one identical top-level lifecycle API.

These are convergence concerns, not evidence of duplicate Flow OS implementations.

## 6. Documentation regression guard

A48.1 adds an executable test that requires architecture truth to:

- include A46/A47 documents;
- name current Brain memory / critics / scorecard owners;
- keep canonical Flow OS ownership explicit;
- keep the two provider entry paths explicit as remaining debt;
- reject the stale exact claims that Brain OS, multi-critic orchestration and Brain scorecard are still unimplemented.

The test protects architecture truth without making documentation a runtime policy owner.

## 7. Scope boundary

A48.1 changes architecture documentation and documentation-truth tests only.

It does not:

- change provider transport;
- change flow selection;
- change lifecycle execution;
- change evidence or gate semantics;
- change memory/scorecard behavior;
- merge/deploy/release target products.

## 8. Acceptance criteria

A48.1 is complete when:

- [x] README architecture index includes A46/A47/A48 current docs;
- [x] Current Runtime Map reflects implemented Brain/critic/memory/scorecard capabilities;
- [x] resolved stale “not implemented” claims are removed;
- [x] provider/lifecycle convergence remains explicitly documented as active debt;
- [x] canonical Flow OS/evidence/evaluation ownership remains explicit;
- [x] executable documentation-truth guard prevents regression to the stale claims;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 9. Handoff

After A48.1 is green and merged, A48.2 should perform **provider capability reconciliation**. It should first create an explicit parity/capability map and adapter tests between `core/runtime/free_provider.py` and the canonical managed `ProviderStageRequest` / `ProviderStageResponse` lane. Do not delete or replace a working provider path before parity is proven.
