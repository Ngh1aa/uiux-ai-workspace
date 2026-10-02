# Architecture Truth Index

Status: **CURRENT THROUGH FLOW 4 / A54.1 / FINAL REGRESSION PASS / FIVE-RECORD KNOWLEDGE OS / FINAL OWNER REVIEW NEXT**  
Audit date: **2026-10-02**  
Baseline before Flow 4 / A54.1: `main@aa48aa49313d5accfb4acf674e38f42441c4c6d2`

This directory is the current architecture truth for UIUX Factory / Flow OS / Brain OS. Current executable source, validators, CI receipts and tests win when historical notes describe an earlier topology.

## Read order

1. `CURRENT-RUNTIME-MAP.md` — current executable topology, ownership and explicit holds.
2. `MIGRATION-BOUNDARIES.md` — runtime/Brain ownership boundaries.
3. `A40-ARCHITECTURE-RECONCILIATION.md` + `A40-ARCHITECTURE-GUARDRAILS.md` — architecture invariants.
4. A41–A47 — Brain contracts, routing/JIT, critics/repair, memory, evidence relationships and scorecard.
5. A48 — provider capability reconciliation and architecture-truth history.
6. A49 — lifecycle contract reconciliation and read-only projection parity.
7. A50 — Knowledge OS architecture, bounded retrieval and current five-record canonical state.
8. `A50-GENAI-NIST-FRESHNESS-REVIEW.md` — current GenAI/NIST freshness HOLD.
9. `A51-PROVIDER-DEFAULT-MIGRATION-READINESS.md` — provider live-evidence HOLD; `legacy` remains default.
10. `A52-LIFECYCLE-MUTATION-CONVERGENCE-READINESS.md` — six semantic blockers and separate lifecycle mutation owners.
11. `A52-LIFECYCLE-EVENT-INTEROPERABILITY.md` — observation-only lifecycle receipts.
12. `A52-POST-INTEROP-EXECUTABLE-DEBT-AUDIT.md` — historical executable-debt selection evidence.
13. `A53-RUNTIME-COMPATIBILITY-CONVERGENCE.md` — Flow 1, first-party compatibility convergence to 0/0.
14. `A53-COMPATIBILITY-SURFACE-GOVERNANCE.md` — Flow 2, criteria-based eight-shim sunset governance.
15. `A53-ARCHITECTURE-DEBT-CLOSURE-AUDIT.md` — Flow 3, 4 CLOSED / 5 INTENTIONAL_HOLD / 0 NEW_ACTIONABLE_DEBT.
16. `A54-FINAL-REGRESSION-CROSS-PROJECT-DOGFOOD.md` — Flow 4, four-project exact-SHA final regression gate.

Historical/current truth anchors retained for A48 regression coverage:

```text
A46-TYPED-BRAIN-MEMORY.md
A46-MEMORY-RECALL-CONTEXT.md
A46-MEMORY-BOUNDARY-BENCHMARK.md
A47-BRAIN-SCORECARD.md
A47-SCORECARD-BENCHMARK.md
A48-ARCHITECTURE-TRUTH-RECONCILIATION.md
```

## Current executable ownership

Shared Flow OS owner:

```text
uiux-factory/core/runtime/flow_os/
```

`skills_UIUX/` owns declarative skills, flows, runtime policy, schemas and reusable Knowledge OS content. Python under `skills_UIUX/runtime/` is compatibility-only and is not independent runtime authority.

Canonical current-run evidence truth:

```text
core/runtime/flow_os/evidence.py
core/provenance/
uiux-factory/qa/
```

Canonical terminal evaluator:

```text
core/evaluation/run_evaluator.py
```

Lifecycle completion without sufficient trusted PASS evidence remains `insufficient_evidence`; provider/model/Brain/Knowledge/observation channels cannot manufacture PASS or release authority.

## Flow 1 / A53.1

Historical A52.3 compatibility census was 8 first-party consumer files / 19 deprecated `runtime.*` imports. Flow 1 migrated all known first-party consumers to canonical `core.runtime.flow_os.*` imports while retaining all eight thin wrappers.

Current truth:

```text
internal_consumer_files = 0
internal_consumer_imports = 0
shim_count = 8
shim_contract_clear = true
identity_checks_clear = true
FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS
```

## Flow 2 / A53.2

All eight public wrappers remain `DEPRECATE_WITH_SUNSET`:

```text
retain_indefinitely = 0
deprecate_with_sunset = 8
open_removal_governance = 0
external_usage_status = UNKNOWN
earliest_removal_review_date = 2026-12-31
removal_governance_open = false
shim_deletion_allowed = false
```

Zero internal consumers does not prove external removal safety.

## Flow 3 / A53.3

Current architecture-debt ledger:

```text
CLOSED = 4
INTENTIONAL_HOLD = 5
NEW_ACTIONABLE_DEBT = 0
ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE
```

Closed areas:

1. Runtime / Flow OS canonical ownership.
2. Brain OS authority boundary.
3. Five-record canonical Knowledge OS baseline.
4. Evidence and terminal-evaluation ownership.

Intentional non-blocking holds:

1. Provider-default migration — real sanitized A51.1 8/8 live matrix required.
2. Lifecycle mutation convergence — six A52.1 semantic blockers remain.
3. GenAI/NIST expansion — official NIST framework-status trigger required.
4. Vector/semantic retrieval — explicit product need + comparative benchmark required.
5. Compatibility-shim removal — fresh external/downstream audit no earlier than 2026-12-31 plus explicit owner removal task.

## Flow 4 / A54.1

Executable owner set:

```text
benchmarks/final-upgrade-regression-v1.json
core/benchmarks/final_upgrade_regression.py
scripts/validate_final_upgrade_regression.py
tests/test_final_upgrade_regression_a54.py
.github/workflows/a20-release-candidate.yml
```

Representative exact-SHA matrix:

```text
Nova     e206f51f2fda006adcf52497d8b827e048e157ec
Lumen    219f3e49f9956290ef69a2e49cb91fefddd5f561
CENNEXT  273403accf8979608fbb16dbe2741cedb0430fb6
LuxRoom  37e6a8c4a2aecdb9cefd9fd4291b353252d5356b
```

Repository-only CI intentionally derives:

```text
HOLD_FINAL_REGRESSION_EVIDENCE_REQUIRED
```

because external project receipts do not exist in that lane. A20 checks out all four pinned projects, runs project-agnostic dogfood, runs structural/security audit, and then aggregates the real JSON receipts.

The required final decision is:

```text
WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS
```

A valid Flow 4 PASS requires:

```text
Flow 3 remains 4 CLOSED / 5 INTENTIONAL_HOLD / 0 NEW_ACTIONABLE_DEBT
release audit passed
Nova dogfood passed exact SHA / expected Flow / truth boundary
Lumen dogfood passed exact SHA / expected Flow / truth boundary
CENNEXT dogfood passed exact SHA / expected Flow / truth boundary
LuxRoom dogfood passed exact SHA / expected Flow / truth boundary
projects = 4 / 4
```

Generic dogfood remains deliberately bounded:

```text
browser.status = NOT_RUN
provider_reasoning.status = NOT_RUN
human_review.status = pending
human_review.verdict = null
release.status = NOT_ATTEMPTED
```

Flow 4 therefore validates source grounding, task-contract inference, declarative Flow routing and cross-project isolation without fabricating browser, provider-quality, aesthetic-human-review, usability, deploy or release evidence.

## Provider boundary

A48 historically reconciled **different provider entry/capability contracts**. Current anchors remain:

```text
core/runtime/free_provider.py
core/runtime/provider_compat_contract.py
core/runtime/flow_os/provider*.py
core/runtime/flow_os/factory_provider_adapter.py
```

Current provider truth remains:

```text
legacy = default
managed_compat = explicit opt-in
no automatic cross-lane fallback
A51.1 live receipts = 0 / 8
KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED
```

Flow 4 does not clear this hold.

## Lifecycle boundary

A49 reconciles **distinct top-level lifecycle APIs** through read-only projection. Current mutation owners remain:

```text
Factory -> core.runtime.run_context.RunContext
Managed -> core.runtime.flow_os.managed.ManagedWebsiteRun
```

The managed CLI shares canonical Flow OS and is **not a second Flow OS**.

Six A52.1 blockers remain:

```text
distinct_state_models
factory_append_only_chronology
managed_checkpoint_and_stage_lineage
managed_human_gate_semantics
replan_invalidation_semantics_non_parity
finalize_release_semantics_non_parity
```

A52.2 event interoperability remains observation-only with execution/authority/gate/evidence/release effects all `none`.

## Brain OS boundary

Brain OS remains a bounded reasoning/control layer, not a third runtime. Implemented anchors include:

```text
core/brain_os/contracts.py
core/brain_os/reasoning/evidence_graph.py
core/brain_os/critics/
core/brain_os/repair_orchestrator.py
core/brain_os/memory_contracts.py
core/memory/brain_memory.py
core/brain_os/adapters/memory_context.py
core/brain_os/scorecard.py
```

Memory, critique, repair proposals, scorecards and retrieved knowledge remain advisory/proposal channels and cannot override canonical runtime evaluation.

## Knowledge OS boundary

Canonical owners:

```text
skills_UIUX/knowledge/
skills_UIUX/knowledge/index.json
skills_UIUX/schemas/knowledge-*.schema.json
core/brain_os/knowledge_retrieval.py
core/brain_os/adapters/knowledge_context.py
```

The canonical corpus remains exactly five records:

```text
financial-services
art-culture
industrial-services
mobility-ev
education-edtech
```

Retrieval remains deterministic metadata-first, bounded, provenance-bearing, advisory-only and vector-free. GenAI/NIST remains `KEEP_HOLD_FRESHNESS_REVIEW`.

## Standing owner delegation

Canonical delegation remains:

```text
benchmarks/governance-owner-delegation-v1.json
```

Mandatory failures may not be bypassed; independent-human review cannot be fabricated; protected history, secrets and repository permissions remain outside delegated continuation.

## Final owner review boundary

Flow 4 PASS is the trigger that allows the previously deferred broad owner review to begin. Flow 4 itself does not fabricate or pre-record that final owner verdict.

Current successor after exact-final-head Flow 4 PASS:

```text
Final Broad Owner Review / Upgrade Closure
```

The five intentional holds remain explicit after upgrade regression completion and are reopened only by their own evidence triggers.

## Source-of-truth priority

When documents disagree:

1. current executable source and tests;
2. exact-head CI/A20 evidence;
3. root `AGENTS.md`, runtime policy and ownership contracts;
4. this architecture truth set;
5. historical A-series notes.
