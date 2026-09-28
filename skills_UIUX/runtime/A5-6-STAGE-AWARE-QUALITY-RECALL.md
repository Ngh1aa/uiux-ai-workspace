# A5.6 — Stage-Aware Quality Recall Routing

Status: **CANONICAL RUNTIME CONTRACT**

A5.6 refines the A5.5 advisory quality recall path so post-render history is delivered only to specialist stages that can act on rendered/UI quality. It prevents project-scoped visual memory from becoming noisy global context.

## Problem closed by A5.6

A5.5 correctly attached `prior_quality_insight` only after canonical flow selection, but the managed run context could still make that quality history visible to every specialist stage.

That is too broad:

- research should establish current project truth from current evidence;
- historical post-render patterns are implementation/QA hints, not research evidence;
- a replan that returns to research must not carry visual-memory context backward into research reasoning.

## Executable ownership

```text
uiux-factory/core/runtime/flow_os/managed.py
```

A5.6 does not create a second memory store or a second planner.

## Canonical routing order

```text
current task/context
→ strip caller-supplied advisory memory keys
→ canonical FlowPlanner
→ resolved flow
→ load bounded quality recall onto manager checkpoint
→ start specialist stage
→ route quality recall by stage agent
```

Quality recall eligibility is currently:

```text
implementation → allowed
qa             → allowed
research       → denied
```

The routing decision is deterministic runtime policy; providers do not decide whether memory is injected.

## Manager checkpoint boundary

Before an eligible stage starts, `prior_quality_insight` remains on the manager checkpoint and is intentionally absent from the general managed task context.

This prevents research/planning providers from seeing visual/post-render history merely because the project has prior quality memory.

## Eligible-stage injection

When an `implementation` or `qa` stage starts:

- the runtime reads the bounded `prior_quality_insight` from the manager checkpoint;
- it injects a copy into the active managed task context;
- it injects a copy into the specialist stage checkpoint;
- the payload remains advisory only.

This makes the hint available to the provider/tool loop for the stage that can actually inspect or repair UI quality.

## Ineligible-stage removal

When a stage whose agent is not quality-recall eligible starts, the runtime removes `prior_quality_insight` from the managed task context and does not copy it into the stage checkpoint.

This rule also applies after lifecycle changes. In particular:

```text
implementation/qa
→ replan
→ research
```

must remove quality recall again. Memory may not become sticky across stage transitions.

## Authority and gate boundary

Stage routing does not alter:

- resolved flow;
- flow revision;
- role authority;
- tool permissions;
- human approvals;
- evidence requirements;
- gate state;
- replan policy;
- merge authority;
- release authority.

The quality payload continues to declare:

```text
authority_effect = none
flow_effect      = none
replan_effect    = none
gate_effect      = none
evidence_effect  = none
merge_effect     = none
release_effect   = none
```

## Relationship to A5.4–A5.5

```text
A5.4  safe post-render quality learning
A5.5  bounded advisory quality recall
A5.6  stage-aware routing of that recall
```

A5.6 does not broaden what is stored or recalled. Raw prose, screenshots, DOM/HTML, source code, prompts, provider/model narrative, evidence files, fingerprints and arbitrary artifacts remain excluded by the earlier A5.4/A5.5 boundaries.

## Verification

Regression coverage must prove at least:

1. a research stage never receives `prior_quality_insight`;
2. the manager checkpoint may retain the bounded recall while research remains clean;
3. an implementation stage receives the bounded advisory recall when it starts;
4. a run returning from implementation/QA to research removes the quality recall again;
5. quality routing does not change the run authority or resolved flow contract;
6. A5.5 flow-selection and replan-injection defenses remain intact.

## Trust model

```text
current research/runtime observation = current evidence
historical quality memory            = implementation/QA advisory hint
```

Historical quality memory may guide **where implementation or QA should inspect**. It never tells research **what is true now** and never substitutes for current rendered evidence.
