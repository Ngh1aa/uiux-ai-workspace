# A8 — Just-in-Time Skill Context

A8 narrows provider context without changing Flow ownership, runtime authority, gate semantics or release policy.

## Problem

Flow OS already performs progressive disclosure between stages: research does not receive implementation/QA knowledge, and QA receives its own routed skills. Before A8, however, every skill routed to the active stage was loaded into every provider request, including conditional or corrective skills that might never be needed.

That produced avoidable context/token pressure and made a large stage behave more like a broad prompt bundle than a just-in-time specialist runtime.

## Contract

A8 keeps the existing `ResolvedStage.skills` contract intact for compatibility. The full list still means:

> these are the capabilities the Flow has routed to this stage.

Provider context is now split at request time:

```text
Flow-routed stage.skills
├─ mandatory/default skills → always loaded
└─ non-mandatory routed skills → JIT pool
                              ↓
                    activate_skill_context
                              ↓
                   loaded on next provider turn
```

`mandatory_skills` remain the role defaults plus flow-required skills. Everything already routed in `stage.skills` but not mandatory is eligible for the JIT pool. This includes context-matched conditional skills and bounded replan additions.

The provider cannot discover or activate arbitrary library skills. The Flow must have routed the skill first.

## Provider-facing metadata

Each provider request receives bounded metadata at:

```text
task_context.jit_skill_context
```

It includes:

- `mandatory_skills` — already active knowledge;
- `active_jit_skills` — previously activated JIT knowledge;
- `available_jit_skills` — exact Flow-routed names that may be activated;
- `max_active_per_stage` — policy-owned activation ceiling;
- explicit `authority_effect=none`, `gate_effect=none`, and `evidence_effect=none` markers.

The provider sees skill names before activation, not arbitrary skill bodies from the whole library.

## Activation tool

`activate_skill_context` is a read-authority context operation. It accepts exactly one skill name from `available_jit_skills`.

Activation:

1. validates the requested name against the current resolved Flow stage;
2. validates the stage activation ceiling from runtime policy;
3. persists only the activated skill name in the stage checkpoint;
4. exposes the corresponding already-routed skill document on the **next** provider request.

Activation does not write project files, change Flow routing, escalate authority, satisfy a gate, create trusted runtime evidence, merge, deploy or release.

A provider request for a skill outside the current JIT pool fails closed.

## Evidence boundary

Skill activation is context state, not evidence.

`ProviderManagedRunner._execute_actions()` deliberately does **not** call `evidence_from_tool()` for `activate_skill_context`. The activation may be recorded in the provider observation/trace stream for debugging, but it cannot enter `evidence_records` and therefore cannot satisfy `gate_evidence_errors()`.

This preserves the A4/A5 rule that model/runtime context management is not proof of product correctness.

## Bounded context

Runtime policy owns the ceiling:

```json
{
  "jit_skill_context": {
    "enabled": true,
    "max_active_per_stage": 6
  }
}
```

The provider cannot raise this value through task text, provider output, memory or tool arguments.

When JIT skill context is disabled, the runner falls back to the pre-A8 behavior and eagerly loads all Flow-routed stage skills. This feature toggle provides a conservative rollback path without changing flow files.

## Replanning

A replan may add corrective skills to a stage only through the existing declarative `ReplanningEngine`. Because replan additions enter `stage.skills` but do not become `mandatory_skills`, they naturally become JIT-eligible on the replanned stage.

The provider cannot use activation to simulate a replan or broaden the Flow.

## Compatibility invariants

A8 intentionally does not redefine these existing contracts:

- `ResolvedStage.skills` still contains every routed skill;
- role `default_skills` stay mandatory;
- flow-required skills stay mandatory;
- existing flow validators and replan checks continue to inspect `stage.skills`;
- provider authority remains bounded by role + managed authority;
- gate/release evidence rules are unchanged.

Regression coverage lives in `uiux-factory/tests/test_jit_skill_context_a8.py`.
