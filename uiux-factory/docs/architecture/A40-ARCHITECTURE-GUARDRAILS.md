# A40.2 — Architecture Guardrails

Status: **IMPLEMENTED / CI-ENFORCED ON PR**  
Date: **2026-10-02**  
Depends on: `A40-ARCHITECTURE-RECONCILIATION.md`

## 1. Purpose

A40.2 converts the architecture boundaries reconciled in A40.1 into executable regression tests before any Brain Core Contracts are added.

This phase does **not** implement Brain OS behavior. It prevents future Brain work from accidentally creating a third runtime, duplicating canonical owners, weakening trusted-evidence semantics or introducing a competing authority/provider policy surface.

Canonical executable test:

```text
uiux-factory/tests/test_architecture_guardrails_a40.py
```

The test is included automatically by the existing `UIUX Factory CI` foundation suite because that workflow runs the full `uiux-factory/tests` directory.

## 2. Guarded invariants

### G1 — Single executable Flow OS owner

The shared executable Flow OS remains:

```text
uiux-factory/core/runtime/flow_os/
```

The test asserts the runtime owner constant and canonical directory.

### G2 — Legacy runtime Python remains compatibility-only

The following compatibility files under `skills_UIUX/runtime/` must continue importing canonical Factory implementations and must not define executable classes or functions:

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

This protects the completed A4 consolidation from slowly regressing into two runtime implementations.

### G3 — Provider claims never become gate evidence

`provider_claim` records remain untrusted context. A model/provider statement such as “the rendered UI passed” cannot satisfy a gate requiring `browser_render` or another trusted runtime evidence type.

### G4 — Memory cannot become current-run evidence

Project/evaluation memory remains advisory. A prior PASS stored as memory cannot be promoted into trusted current-run evidence and cannot satisfy a current validator/browser gate.

### G5 — Brain OS cannot redefine canonical runtime owners

When `uiux-factory/core/brain_os/` is introduced, it may not define replacement implementations for canonical owner symbols such as:

```text
FlowPlanner
GoalInterpreter
TaskContract
ManagedFlowController
ProviderManagedRunner
ProviderNeutralAgentHarness
ProductionReleaseController
EvidenceRecord
```

Brain OS must adapt or call the canonical owner instead.

### G6 — Brain OS cannot directly own execution/release/provider authority

Future Brain modules are forbidden from directly importing execution-authority surfaces including:

```text
core.runtime.free_provider
core.runtime.flow_os.file_tools
core.runtime.flow_os.provider
core.runtime.flow_os.provider_runner
core.runtime.flow_os.release
core.runtime.flow_os.sandbox
core.runtime.flow_os.target_runner
core.runtime.flow_os.workspace
```

The Brain is a reasoning/control layer. Runtime actions remain behind canonical adapters and authority boundaries.

### G7 — Brain Evidence Graph must adapt existing evidence primitives

If future Brain work adds:

```text
core/brain_os/reasoning/evidence_graph.py
```

it must also provide:

```text
core/brain_os/adapters/evidence.py
```

and that adapter must reference the existing runtime evidence backbone plus current provenance/release lineage primitives.

Brain OS is forbidden from redefining its own `EvidenceRecord` or `TRUSTED_EVIDENCE_TYPES` authority.

### G8 — No third runtime/provider/release policy file

`core/brain_os/` may not introduce independent files named:

```text
runtime-policy.json
provider-policy.json
release-policy.json
```

Canonical policy remains owned by `skills_UIUX/runtime/runtime-policy.json` and existing release/runtime contracts.

## 3. Why future-aware tests exist before Brain OS exists

Some A40.2 tests inspect `core/brain_os/` only if that directory exists. This is intentional:

- today they establish a passing architecture baseline;
- A41+ can introduce Brain modules incrementally;
- the same tests then become active constraints without needing to rewrite the architecture contract after every Brain phase.

A missing Brain package is therefore not considered proof that Brain architecture is correct; the tests also actively validate current runtime/evidence/memory invariants that already exist.

## 4. Test design rules

The guardrails intentionally test stable ownership and trust boundaries rather than exact documentation wording.

They do not:

- require Brain implementation before A41;
- duplicate product behavior tests;
- assert aesthetic quality;
- declare runtime QA PASS from documentation;
- block legitimate `adapters/flow_os.py`, `adapters/factory.py` or `adapters/evidence.py` layers;
- prevent future provider adapters at the canonical provider capability boundary;
- change release/merge authority.

## 5. A40.2 acceptance criteria

A40.2 is complete when:

- [x] single executable Flow OS ownership is executable-test protected;
- [x] compatibility shims cannot accumulate new classes/functions unnoticed;
- [x] provider claims cannot satisfy trusted gates;
- [x] memory cannot satisfy current-run gates;
- [x] future Brain modules cannot redefine canonical owners;
- [x] future Brain modules cannot directly import execution/release authority surfaces;
- [x] future Brain Evidence Graph is forced through an adapter to existing evidence/provenance primitives;
- [x] Brain cannot add a third runtime/provider/release policy file;
- [ ] PR CI is green on the final A40.2 head.

## 6. Handoff to A41

After the final A40.2 head passes CI, A41 may introduce only data/control contracts first:

```text
BrainTaskFrame
Hypothesis
Decision
Uncertainty
CritiqueIssue / RepairLink
```

A41 must not add execution tools, provider ownership, release authority, a new gate engine or a parallel evidence truth store.
