# A8.2 — JIT Provenance & Optional Skill Routing

A8.2 closes the remaining declarative gap in A8: `optional_skills` existed in the Flow schema and validator, but the canonical `SkillResolver` did not route them into any runtime pool.

It also stops the provider runner from reconstructing JIT eligibility indirectly as `stage.skills - mandatory_skills`.

## Resolved stage contract

`ResolvedStage` now stores three related views explicitly:

```text
skills                 all capabilities routed to the stage
mandatory_skills       role defaults + flow required skills; eagerly loaded
jit_skills             bounded deferred capabilities eligible for activation
jit_skill_sources      deterministic provenance for each JIT skill
```

Allowed provenance values are:

- `optional` — declared by the Flow under `optional_skills`;
- `conditional` — matched a declarative `conditional_skills.when` rule;
- `additional` — explicitly supplied to the canonical planner as an additional skill;
- `replan` — added by the bounded declarative replanning engine;
- `legacy_inferred` — reconstructed only when loading a pre-A8.2 checkpoint that has no explicit JIT metadata.

Mandatory skills may never overlap the JIT pool. JIT skills must remain a subset of `skills`. Unknown provenance values or provenance entries for non-JIT skills fail closed.

## Optional skills are now live

A Flow stage may declare:

```json
{
  "required_skills": ["project-context"],
  "optional_skills": ["ecommerce-website"]
}
```

The optional skill is routed into `skills` and `jit_skills`, but not into `mandatory_skills`. Its body therefore remains unloaded until the provider activates it through `activate_skill_context`.

This gives `optional_skills` a concrete runtime meaning without increasing stage authority or eagerly expanding provider context.

## Conditional and additional skills

Matched conditional skills and planner-level additional skills follow the same deferred contract. Their provenance is recorded as `conditional` and `additional` respectively.

Duplicate capabilities are de-duplicated deterministically. A capability already mandatory never becomes JIT merely because it also appears in optional/conditional/additional declarations.

## Replanning

When a declarative replan adds a non-mandatory skill, the skill enters both `stage.skills` and `stage.jit_skills` with provenance `replan`.

When a replan drops a JIT skill, the capability is removed from:

- `stage.skills`;
- `stage.jit_skills`;
- `stage.jit_skill_sources`.

Mandatory/default skills remain protected by the existing replanning invariant.

## Provider boundary

`ProviderManagedRunner` consumes `stage.jit_skills` directly. It no longer decides eligibility by subtracting mandatory skills from the full capability list.

Provider-facing metadata exposes the bounded provenance map:

```text
task_context.jit_skill_context.jit_skill_sources
```

Activation results also report the selected skill's source for trace/debug visibility.

Provenance is descriptive only. It has:

```text
authority_effect=none
gate_effect=none
evidence_effect=none
```

and cannot become trusted evidence, alter Flow routing, authorize merge/release, or expand the JIT pool.

## Backward checkpoint compatibility

Managed runs created before A8.2 do not contain `jit_skills` or `jit_skill_sources`.

`ResolvedStage.__post_init__()` migrates those records conservatively by reconstructing the old A8 rule:

```text
legacy JIT pool = skills - mandatory_skills
```

Each reconstructed entry is marked `legacy_inferred`.

This preserves in-flight managed runs while making every newly resolved stage explicit going forward.

## Regression coverage

`uiux-factory/tests/test_jit_skill_provenance_a8_2.py` covers:

- optional skill routing;
- conditional/additional provenance;
- missing optional skill fail-closed behavior;
- pre-A8.2 checkpoint migration;
- invalid provenance rejection;
- replan add/drop lineage;
- provider runner use of the explicit JIT pool rather than set-difference inference.
