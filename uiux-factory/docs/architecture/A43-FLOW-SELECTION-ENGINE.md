# A43.1 — Flow Selection Engine

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A40 Architecture Guardrails + A41 Brain contracts + A42 Evidence Integrity

## 1. Purpose

A43.1 exposes canonical Flow OS selection to Brain OS without creating a second planner.

Brain OS may classify/record task surface, ask the canonical planner for a declarative flow, and propose a bounded one-rung escalation when the current surface is demonstrably too narrow.

Canonical adapter:

```text
core/brain_os/adapters/flow_selection.py
```

Canonical owners remain:

```text
core/runtime/flow_os/adaptive_surface.py::classify_change_surface
core/runtime/flow_os/flow.py::FlowPlanner
core/runtime/flow_os/flow.py::FlowResolver
```

Executable tests:

```text
tests/test_brain_flow_selection_a43.py
tests/test_architecture_guardrails_a40.py
```

## 2. Smallest-flow-first rule

A43.1 preserves the established change-surface ladder:

```text
MICRO
→ FOCUSED
→ PAGE
→ REDESIGN
→ PRODUCT
```

When a canonical Task Contract already contains `change_surface`, the adapter preserves it.

When it is absent, Brain calls the existing canonical classifier:

```text
classify_change_surface(goal, intent, scope)
```

The resulting surface is then supplied to the existing `FlowPlanner.plan()` owner.

Examples:

```text
one card / spacing defect
→ MICRO
→ micro-ui-change

one section / component cluster
→ FOCUSED
→ existing-ui-improvement

one route / page
→ PAGE
→ page-ui-work

whole website redesign
→ REDESIGN
→ professional-website-redesign

broad portfolio system
→ REDESIGN or PRODUCT + website_type=portfolio
→ portfolio-career-system
```

The declarative flow JSON remains the routing policy. Brain does not hard-code flow IDs as execution rules.

## 3. FlowSelectionDecision

`FlowSelectionDecision` is a strict immutable advisory record containing:

```text
change_surface
surface_source
flow_id
flow_source
score
canonical_owner
classifier_owner
rationale
```

It records a selection already made by canonical Flow OS.

It does not:

- create or execute stages;
- change runtime authority;
- satisfy gates;
- mutate flow JSON;
- replace `FlowPlanner`;
- choose providers/models;
- merge/deploy/release.

## 4. Bounded escalation

A43.1 introduces `FlowEscalationProposal` for one-rung widening only:

```text
MICRO → FOCUSED
FOCUSED → PAGE
PAGE → REDESIGN
REDESIGN → PRODUCT
```

The following are rejected:

```text
MICRO → PAGE
FOCUSED → PRODUCT
PRODUCT → anything wider
```

Allowed triggers are bounded:

```text
SCOPE_INSUFFICIENT
REQUIRED_STAGE_MISSING
EVIDENCE_REVEALED_BROADER_SCOPE
```

Evidence-driven escalation requires at least one evidence reference.

A proposal cannot mutate a running flow. To re-select after escalation, the widened context is resubmitted through canonical `FlowPlanner.plan()`.

## 5. Authority boundary

A43.1 intentionally does **not** define:

```text
class FlowPlanner
class FlowResolver
class GoalInterpreter
```

It does not modify:

```text
skills_UIUX/flows/*.json
skills_UIUX/runtime/runtime-policy.json
core/runtime/flow_os/flow.py
core/runtime/flow_os/adaptive_surface.py
```

Therefore Brain remains a reasoning/control layer above Flow OS.

## 6. Acceptance criteria

A43.1 is complete when:

- [x] missing task surface is classified through canonical `classify_change_surface`;
- [x] an existing Task Contract surface is preserved;
- [x] flow resolution goes through canonical `FlowPlanner.plan()`;
- [x] micro/focused/page/redesign/product representative tasks select the intended declarative lane;
- [x] portfolio broad work still routes through the portfolio-specific flow when applicable;
- [x] escalation is adjacent-only;
- [x] evidence-driven escalation requires evidence references;
- [x] escalation source must match current context;
- [x] no Brain-owned FlowPlanner/FlowResolver/execution runtime is introduced;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 7. Handoff

After A43.1 is green and merged, A43.2 should implement **JIT Context Loader** by adapting the existing `SkillResolver` and runtime JIT context limits:

```text
required/default skills
+ conditional/optional/additional JIT skills
+ context budget
```

A43.2 must not create a second skill router or allow Brain/memory/provider output to bypass canonical routed-skill boundaries.
