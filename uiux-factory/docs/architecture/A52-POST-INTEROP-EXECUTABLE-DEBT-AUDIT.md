# A52.3 — Post-Interop Executable Debt Audit

Status: **IMPLEMENTED / VERIFICATION PENDING**  
Date: **2026-10-02**  
Baseline: `main@c8818fd9b616e9dd4dfe9d70bda79d930448a383`  
Depends on: A52.2 Lifecycle Event Interoperability Contract

## Purpose

A52.3 exists to prevent architecture work from advancing by phase numbering alone.

After A52.2, the repository has several known debt areas, but most are intentionally blocked by executable governance. A52.3 therefore performs a read-only executable debt selection audit before authorizing any successor package.

It does not modify runtime behavior.

## Inputs

The audit reads current executable truth from:

```text
benchmarks/provider-default-migration-readiness-v1.json
benchmarks/provider-live-trial-receipts-v1.json
benchmarks/lifecycle-mutation-convergence-readiness-v1.json
benchmarks/lifecycle-event-interop-v1.json
benchmarks/knowledge-genai-nist-freshness-review-v1.json
benchmarks/knowledge-canonical-state-v3.json
skills_UIUX/runtime/*.py
active first-party Python consumers under uiux-factory/ and skills_UIUX/scripts/
```

Executable owner:

```text
core/benchmarks/post_interop_executable_debt_audit.py
```

Validator:

```text
scripts/validate_post_interop_executable_debt_audit.py
```

## Blocked/deferred candidates

A52.3 confirms these are **not** eligible as the next implementation package:

### Provider default migration

```text
current default = legacy
live receipts = 0 / 8
collection_status = NOT_RUN
```

A51.1 therefore remains fail-closed. A52.3 does not change provider routing or defaults.

### Lifecycle mutation convergence

All six A52.1 blockers remain:

```text
distinct_state_models
factory_append_only_chronology
managed_checkpoint_and_stage_lineage
managed_human_gate_semantics
replan_invalidation_semantics_non_parity
finalize_release_semantics_non_parity
```

A52.2 improves observability only. It does not clear mutation governance.

### GenAI/NIST expansion

A50.14 remains:

```text
KEEP_HOLD_FRESHNESS_REVIEW
```

No draft, acceptance trial, canary, canonical promotion or index mutation is opened by A52.3.

### Vector / semantic retrieval

Canonical Knowledge OS governance still keeps:

```text
vector_search_change_allowed = false
```

Vector/semantic retrieval remains deferred.

## Compatibility-shim audit

The only currently actionable internal executable debt identified by A52.3 is the deprecated compatibility surface under:

```text
skills_UIUX/runtime/
```

The eight shims remain thin compatibility wrappers and contain no independent decision/runtime logic:

```text
adaptive_surface.py
agent.py
flow.py
manager.py
mcp_server.py
provider.py
provider_runner.py
task_context.py
```

Their canonical implementation targets remain under:

```text
uiux-factory/core/runtime/flow_os/
```

## First-party consumer census

A52.3 performs an AST-based scan over active first-party Python under:

```text
uiux-factory/
skills_UIUX/scripts/
```

The current exact census is:

```text
8 consumer files
19 deprecated runtime.* module imports
```

Current consumers:

```text
uiux-factory/tests/test_adaptive_flow.py
  runtime.flow
  runtime.task_context

uiux-factory/tests/test_canonical_runtime_a4.py
  runtime.flow
  runtime.manager
  runtime.task_context

uiux-factory/tests/test_runtime_lifecycle_context.py
  runtime.flow
  runtime.task_context

uiux-factory/tests/test_task_contract.py
  runtime.agent
  runtime.flow
  runtime.manager
  runtime.task_context

skills_UIUX/scripts/context-manifest.py
  runtime.agent

skills_UIUX/scripts/validate-flows.py
  runtime.flow

skills_UIUX/scripts/validate-provider-runtime.py
  runtime.agent
  runtime.manager
  runtime.provider
  runtime.provider_runner

skills_UIUX/scripts/validate-runtime-foundation.py
  runtime.agent
  runtime.manager
```

This census is now an exact regression contract. A new, removed or changed first-party shim consumer causes A52.3 validation to fail rather than silently changing the migration boundary.

## Decision

Given the current executable evidence, A52.3 derives:

```text
SELECT_COMPAT_SHIM_RETIREMENT_READINESS
```

Selected successor package:

```text
A53.1 — Runtime Compatibility Shim Retirement Readiness
```

This is **not** permission to delete compatibility shims.

A53.1 should determine whether first-party consumers can migrate to canonical imports while preserving compatibility guarantees, identity/alias behavior, existing CLI/integration expectations and external compatibility surfaces.

## Governance boundary

A52.3 remains audit/selection only:

```text
runtime_mutation_allowed = false
shim_deletion_allowed = false
provider_default_change_allowed = false
lifecycle_state_owner_change_allowed = false
genai_promotion_allowed = false
vector_search_change_allowed = false
product_evidence = false

execution_effect = none
authority_effect = none
gate_effect = none
evidence_effect = none
release_effect = none
```

## Why A53.1 is readiness, not removal

The repository still actively consumes the compatibility imports in first-party tests and scripts. Removing the shims now would convert a cleanup task into an uncontrolled breaking migration.

The safe sequence is:

```text
A52.3 audit
→ prove exact consumers
→ A53.1 retirement readiness / migration planning
→ migrate first-party consumers with parity evidence
→ re-audit zero internal consumers
→ separate removal governance if still justified
```

External users/integrations must not be assumed absent merely because first-party consumer count eventually reaches zero.

## Acceptance criteria

- [x] current blocked/deferred architecture candidates are derived from executable governance;
- [x] all eight compatibility shims are inventoried;
- [x] shims are checked for accidental independent executable logic;
- [x] active first-party Python consumer census is AST-based;
- [x] exact current census is 8 files / 19 imports;
- [x] census is encoded as an exact regression contract;
- [x] A53.1 is selected from evidence rather than phase numbering;
- [x] A52.3 authorizes no runtime/provider/lifecycle/knowledge mutation;
- [ ] exact final PR head passes UIUX Factory CI;
- [ ] exact final PR head passes A20 regression/security/dogfood;
- [ ] PR is mergeable.

## Handoff

After A52.3 is verified and merged, the bounded next architecture package is:

```text
A53.1 — Runtime Compatibility Shim Retirement Readiness
```

A53.1 may audit/migrate first-party consumers only under compatibility-preserving tests. It must not delete the shims merely because A52.3 selected the debt area.
