# A43.2 — JIT Context Loader

Status: **IMPLEMENTED / FINAL VERIFICATION PENDING**  
Date: **2026-10-02**  
Depends on: A43.1 canonical flow selection + existing `SkillResolver` / runtime JIT controls

## 1. Purpose

A43.2 gives Brain OS a strict read-only view of the skill/context envelope already produced by canonical Flow OS.

Brain does not route skills independently. It receives a canonical `ResolvedStage` and projects:

```text
mandatory/default skills
+ routed JIT pool
+ JIT provenance
+ active/available JIT view
+ runtime-policy count/budget ceilings
```

Canonical Brain adapter:

```text
core/brain_os/adapters/jit_context.py
```

Canonical owners remain:

```text
core/runtime/flow_os/flow.py::SkillResolver
core/runtime/flow_os/flow.py::ResolvedStage
skills_UIUX/runtime/runtime-policy.json
core/runtime/flow_os/skill_sections.py::SkillSectionPolicy
core/runtime/flow_os/provider_runner.py runtime activation/preflight
```

## 2. No second skill router

`JITContextPlan` is a projection of an already-resolved stage.

It cannot add a new skill to the routed pool.

It preserves:

```text
mandatory_skills
routed_jit_skills
jit_skill_sources
```

from canonical `ResolvedStage`.

An active JIT skill must already exist in `routed_jit_skills`.

Mandatory skills are always active and cannot be treated as optional JIT activations.

## 3. JIT count budget

The adapter reads the canonical runtime-policy values:

```text
jit_skill_context.enabled
jit_skill_context.max_active_per_stage
```

Current default/production policy value:

```text
max_active_per_stage = 6
```

When JIT is enabled:

- active JIT skills must be a subset of the routed pool;
- active JIT count may not exceed the policy ceiling;
- `available_jit_skills = routed pool - active`.

When JIT is disabled, all routed JIT skills are treated as already active, matching current runtime semantics.

## 4. Provider document context ceiling

`JITContextPlan` exposes the **runtime-policy ceiling**:

```text
provider_context.max_document_chars_per_request
```

Current policy value:

```text
180000 unicode chars
```

This is not a promise that a future provider request will fit.

Runtime remains authoritative because `ProviderManagedRunner` may apply a lower environment ceiling and performs the actual document-load preflight. Brain cannot bypass or raise that runtime ceiling.

## 5. Section-level retrieval budgets

The adapter reuses canonical `SkillSectionPolicy.from_policy(...)` for:

```text
max_sections_per_skill
max_section_chars
max_retrievals_per_stage
max_total_retrieved_chars
max_index_chars
```

This avoids inventing a separate section-retrieval policy in Brain OS.

## 6. JITActivationRequest

`request_jit_activation(...)` creates an advisory request only.

It validates:

- JIT is enabled;
- requested skill is non-empty;
- requested skill is not mandatory;
- requested skill belongs to the canonical routed JIT pool;
- count budget is not already exhausted.

The request explicitly records:

```text
authority_effect = none
gate_effect = none
evidence_effect = none
runtime_preflight_required = true/false
```

A request is **not** an activation receipt. The runtime may still reject it when provider document-budget preflight fails.

## 7. Runtime parity checks

Executable tests compare Brain policy projection with current runtime methods for the same policy document:

```text
ProviderManagedRunner._jit_config()
ProviderManagedRunner._provider_context_budget()
```

This keeps the Brain view pinned to current runtime semantics without importing the provider runner into Brain code.

## 8. Acceptance criteria

A43.2 is complete when:

- [x] Brain projects mandatory/JIT skills from canonical `ResolvedStage`;
- [x] JIT provenance is preserved;
- [x] non-routed skills are rejected;
- [x] mandatory skills cannot be requested as JIT;
- [x] `max_active_per_stage` is enforced before an activation request;
- [x] disabled JIT semantics match runtime behavior;
- [x] provider document policy ceiling is visible but not overridable by Brain;
- [x] section budgets reuse canonical `SkillSectionPolicy`;
- [x] activation requests have no authority/gate/evidence effect;
- [x] tests compare policy projection with current provider-runner semantics;
- [ ] final PR head passes UIUX Factory CI and A20 release-candidate regression/dogfood.

## 9. Handoff

After A43.2 is green and merged, A43.3 should add a **Routing Benchmark** over representative real task prompts.

The benchmark should score:

```text
Task Contract surface
→ selected declarative flow
→ mandatory/JIT skill envelope
```

It must test regressions without becoming another router or changing production routing decisions.
