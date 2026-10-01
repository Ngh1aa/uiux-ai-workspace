# A44.1 — Core Design Critics

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A41 Critique contracts + A42 Evidence Integrity + A43 routing/context layers

## 1. Purpose

A44.1 introduces four bounded Brain OS design critics:

```text
Visual
UX / IA
Design System
Accessibility
```

Every critic is advisory. It may emit `CritiqueIssue(status=OBSERVED)` but cannot:

- mark its own issue `CONFIRMED` or `RESOLVED`;
- satisfy a runtime QA gate;
- manufacture trusted evidence;
- execute repairs;
- mutate source design artifacts;
- choose providers;
- merge/deploy/release.

Canonical implementation:

```text
core/brain_os/critics/core_design.py
```

Executable tests:

```text
tests/test_brain_core_design_critics_a44.py
```

## 2. Existing visual primitive reused

The current repository does not contain a canonical class named `VisualCritic`.

The existing deterministic visual review primitive is:

```text
core/orchestration/visual_brain.py::VisualBrain
```

A44.1 therefore adapts **VisualBrain**, rather than creating a competing visual critic/gate.

`VisualBrainCriticAdapter` calls:

```text
VisualBrain.evaluate(...)
```

and deliberately does **not** call:

```text
VisualBrain.apply_calibration(...)
```

This keeps the Brain critic read-only.

The adapter converts existing failed visual gates and `generic_tells` into advisory `CritiqueIssue` records while preserving upstream status/score only as metadata.

An upstream `VisualBrain.status=passed` does not become a Brain/runtime QA PASS.

## 3. UX / IA Critic

`UXIACritic` reads existing structured contracts only:

```text
DesignContract.ux
VisualComposition.pages
VisualComposition.gates.page_roles_mapped
```

It can observe bounded structural gaps such as:

- missing page roles;
- duplicate page-role names;
- missing primary journey;
- missing route/page structure;
- duplicate route paths;
- blank page roles;
- pages with no section hierarchy;
- source composition reporting page-role mapping as unconfirmed.

It does not invent user research, usability findings or product outcomes.

## 4. Design System Critic

`DesignSystemCritic` reads:

```text
DesignSystemContract
FoundationTokens
ComponentContract
DesignSystemGate
```

It can observe:

- source design-system gates still false;
- unresolved foundation tokens;
- duplicate component identity;
- P0 components without states;
- components without responsive contracts;
- explicitly unresolved design-system debt.

It never changes `DesignSystemGate` values.

## 5. Accessibility Critic

`AccessibilityCritic` is a **contract-level** critic, not a runtime accessibility test.

It can observe:

- accessibility contracts not defined at design-system level;
- P0 components with no accessibility contract;
- interactive components with no state contract;
- thin interaction accessibility notes that omit keyboard/focus/semantic behavior;
- motion tokens without an explicit reduced-motion contract.

These findings are design-contract gaps only.

Runtime browser/DOM/accessibility validation remains owned by existing QA/runtime evidence routes.

## 6. CoreCriticReport

Every critic returns a strict immutable report:

```text
critic_id
issues
reviewed_artifacts
source_owner
upstream_status / upstream_score (optional metadata)
advisory_only = true
authority_effect = none
gate_effect = none
evidence_effect = none
```

The report intentionally has no `passed` field.

Therefore:

```text
issues == []
```

does **not** mean:

```text
QA PASS
validated design
release ready
```

## 7. Relationship to A41/A42

A44.1 emits A41 `CritiqueIssue` objects in `OBSERVED` state.

A later critic/evidence orchestration layer may use A42 canonical evidence references to support or reject findings.

Only then can a finding become evidence-backed through the already-defined A41/A42 lineage:

```text
CritiqueIssue
→ RootCause
→ RepairDirective
→ RetestRequirement
→ canonical evidence
```

A44.1 does not shortcut that chain.

## 8. Acceptance criteria

A44.1 is complete when:

- [x] existing `VisualBrain.evaluate()` is reused rather than rewritten;
- [x] visual review adapter is read-only and never applies calibration;
- [x] UX/IA critic reads current structured UX/composition contracts;
- [x] Design System critic reads current token/component/gate contracts;
- [x] Accessibility critic remains contract-level and does not claim runtime conformance;
- [x] every generated issue begins as `OBSERVED`;
- [x] critic reports cannot self-pass a gate;
- [x] critic reports cannot manufacture evidence/trust/authority;
- [x] source contracts remain unchanged after review;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 9. Handoff

After A44.1 is green and merged, A44.2 should add **Product & Truth Critics**:

```text
Product Critic
Runtime Critic
Evidence / Truth Critic
```

Those critics should reuse A42 evidence integrity and current runtime artifacts rather than duplicating gate/evidence authority.
