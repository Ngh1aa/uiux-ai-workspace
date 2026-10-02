# Architecture Truth Index

Status: **A40–A47 MERGED + A48.1–A48.5 MERGED + A48.6 CONTROLLED PROVIDER LANE IMPLEMENTED**  
Audit date: **2026-10-02**  
Current architecture baseline: `main@abc25946ca37d5b9f155056e616de120b093e9ad`

This directory contains the current architecture truth for UIUX Factory / Flow OS / Brain OS evolution. Current source and executable tests remain authoritative when older A-series prose disagrees with this index.

## Read order

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, owners and remaining convergence debt.
2. `MIGRATION-BOUNDARIES.md` — active post-A4 architecture contract and Brain OS boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` — capability/ownership reconciliation.
4. `A40-ARCHITECTURE-GUARDRAILS.md` — executable architecture invariants.
5. `A41-BRAIN-CORE-CONTRACTS.md` — BrainTaskFrame / Uncertainty / Hypothesis / Decision contracts.
6. `A41-CRITIQUE-REPAIR-CONTRACTS.md` — critique / root-cause / repair / retest contracts.
7. `A42-EVIDENCE-GRAPH-FOUNDATION.md` — adapter-first relationship graph over canonical evidence IDs.
8. `A42-EVIDENCE-INTEGRITY.md` — false-evidence and end-to-end lineage protection.
9. `A43-FLOW-SELECTION-ENGINE.md` — Brain adapter over canonical change-surface / FlowPlanner selection.
10. `A43-JIT-CONTEXT-LOADER.md` — read-only projection of mandatory/JIT skill routing.
11. `A43-ROUTING-BENCHMARK.md` — deterministic routing regression corpus.
12. `A44-CORE-DESIGN-CRITICS.md` — advisory core design critics.
13. `A44-PRODUCT-TRUTH-CRITICS.md` — advisory Product / Runtime / Evidence critics.
14. `A45-CRITIQUE-REPAIR-ORCHESTRATOR.md` — proposal-only critique → repair contracts.
15. `A45-REPAIR-LINEAGE-GRAPH.md` — repair proposal projection into A42 graph.
16. `A45-REPAIR-PROPOSAL-BENCHMARK.md` — proposal-policy regression guard.
17. `A46-TYPED-BRAIN-MEMORY.md` — typed project-scoped rationale / hypothesis / decision memory.
18. `A46-MEMORY-RECALL-CONTEXT.md` — post-routing historical-memory context adapter.
19. `A46-MEMORY-BOUNDARY-BENCHMARK.md` — memory boundary regression guard.
20. `A47-BRAIN-SCORECARD.md` — provenance-aware evaluation/critic/integrity aggregation.
21. `A47-SCORECARD-BENCHMARK.md` — scorecard truth/provenance guard.
22. `A48-ARCHITECTURE-TRUTH-RECONCILIATION.md` — post-A47 architecture reconciliation.
23. `A48-PROVIDER-CAPABILITY-RECONCILIATION.md` — Factory/managed provider capability map.
24. `A48-PROVIDER-ARTIFACT-BRIDGE.md` — bounded optional raw-artifact carrier.
25. `A48-MANAGED-PROVIDER-COMPAT-ADAPTER.md` — opt-in async Factory completion bridge.
26. `A48-PROVIDER-PARITY-DOGFOOD.md` — deterministic provider parity + project-profile compatibility smoke.
27. `A48-CONTROLLED-PROVIDER-LANE.md` — explicit manager opt-in lane with legacy default and run provenance.

## Current architecture statement

A4 runtime consolidation remains in force. The single shared executable Flow OS owner is `uiux-factory/core/runtime/flow_os/`. `skills_UIUX/` remains the declarative owner for skills, flows, policies, schemas and runtime policy. Python modules under `skills_UIUX/runtime/` are compatibility shims, not an independent runtime.

The full Factory product lifecycle remains under `uiux-factory/run.py` + `core/manager/`; the provider-neutral managed CLI uses the same canonical Flow OS through `skills_UIUX/scripts/uiux-agent.py`.

## Brain / evidence / evaluation boundary

Brain OS remains a bounded reasoning/control layer, not a third execution runtime. Canonical evidence remains owned by Flow OS/provenance/QA; canonical terminal evaluation remains `core/evaluation/run_evaluator.py`. Brain graph, critics, repair proposals, typed memory and scorecard cannot replace evidence truth or gate/release authority.

## Provider convergence boundary

A48.2 mapped provider capability gaps. A48.3 added the bounded optional `artifact` carrier. A48.4 added `ManagedArtifactCompletionAdapter`, preserving Factory async `complete(...) -> str` while offloading synchronous managed providers and retaining shared context/call/token/timeout limits. A48.5 added deterministic offline parity plus Nova/Lumen/CENNEXT/LuxRoom profile smoke, explicitly not product evidence.

A48.6 adds the first manager-level selection contract:

```text
UIUX_FACTORY_PROVIDER_LANE
unset / blank  -> legacy
legacy         -> legacy
managed-compat -> ManagedArtifactCompletionAdapter
other          -> fail closed
```

The default remains `legacy`. Managed compatibility is explicit opt-in only. There is no silent fallback, percentage rollout or automatic default migration.

Every AI run records secret-free `provider-lane.json` provenance and mirrors it into `flow-plan.json`. Lane selection has `authority_effect=none`, `gate_effect=none`, `evidence_effect=none`, `release_effect=none`.

Provider transports remain lazy imports inside the AI branch. Template/external execution does not select an internal provider lane.

## Regression and dogfood

Main UIUX Factory CI validates product/routing/repair/memory/scorecard/provider-parity corpora before full pytest. A20 continues full regression, structural/security audit and pinned Nova/Lumen/CENNEXT dogfood. Provider/runtime changes trigger A13 Nova and A14 golden/canary regression where path filters apply.

## Remaining architecture debt

1. Provider convergence is complete only at **controlled opt-in** level. The default remains legacy; any future default migration is a separate evidence-driven decision.
2. Factory product execution (`run.py` + `core/manager/`) and managed CLI execution still expose distinct top-level lifecycle APIs despite sharing canonical routing/runtime owners.
3. A broader declarative Knowledge OS is not implemented as one canonical subsystem; methodology remains correctly owned by `skills_UIUX`.

## Source-of-truth priority

When documents disagree:

1. current source and executable tests;
2. root `AGENTS.md`, runtime policy and `docs/CONTRACT-OWNERSHIP.md`;
3. this architecture truth set;
4. current capability/QA docs that match source;
5. historical A-series plans and implementation notes.

## Next architecture task

After A48.6 is green and merged, move to **A49.1 Lifecycle Contract Reconciliation**. Do not flip the provider default as part of A49.