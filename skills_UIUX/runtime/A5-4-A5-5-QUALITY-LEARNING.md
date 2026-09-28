# A5.4–A5.5 — Post-Render Quality Learning + Advisory Recall

Status: **CANONICAL RUNTIME CONTRACT**

This contract extends the A5.1–A5.3 evaluation-memory foundation without creating a second orchestration path or granting historical memory any execution authority.

## A5.4 — Safe post-render quality learning

A5.4 bridges the canonical Factory post-render evaluator output into project-scoped evaluation memory.

Executable ownership:

```text
uiux-factory/core/memory/quality_pattern_normalizer.py
uiux-factory/core/memory/evaluation_memory.py
uiux-factory/core/verification/post_render_evaluators_final.py
```

Only allowlisted runtime-observed metadata may be persisted:

- evaluator id;
- requirement id;
- categorical outcome;
- applicability;
- bounded test-target identifiers;
- deterministic fingerprint;
- bounded occurrence count.

The learning boundary rejects raw rationale/prose, prompts, provider/model narrative, DOM/HTML, source code, screenshots/raw images, evidence file contents and arbitrary artifacts.

Quality patterns remain advisory only and cannot change PASS/FAIL, prototype acceptance, authority, flow, replan policy, merge or release behavior.

A5.4 must honor the canonical `evaluation_memory.enabled` runtime policy. Post-render code may not hard-code memory on.

## A5.5 — Advisory Quality Pattern Recall

A5.5 adds the read side for A5.4 quality patterns.

Executable ownership:

```text
uiux-factory/core/memory/quality_pattern_recall.py
uiux-factory/core/runtime/flow_os/managed.py
```

The canonical order is:

```text
current task/context
→ remove caller-supplied memory-shaped keys
→ GoalInterpreter / canonical FlowPlanner
→ resolved flow
→ load project-scoped normalized quality patterns
→ build bounded categorical quality insight
→ attach as provider-facing advisory context
→ specialist execution
```

Historical quality memory is therefore attached only **after** flow selection.

## Recall payload

A5.5 may expose only bounded aggregate/categorical fields such as:

- observed pattern count;
- observed occurrence count;
- outcome occurrence counts;
- recurrent attention patterns (`failed` / `cantTell`);
- recurrent passed patterns;
- evaluator id;
- requirement id;
- applicability;
- occurrence count.

The recall payload intentionally excludes:

- deterministic fingerprints;
- test targets;
- raw evidence paths/files;
- rationale/prose;
- prompts;
- provider/model output;
- DOM/HTML;
- source code;
- screenshots/raw images;
- arbitrary artifact contents.

Recall is bounded to the existing evaluation-memory recall budget and an additional hard ceiling in the A5.5 recall module.

## Authority and evidence boundary

`prior_quality_insight` is provider-only advisory history.

It cannot:

- select or alter the canonical flow;
- raise or reduce authority;
- enter canonical replanning policy context;
- satisfy, waive or override a gate;
- count as current-run evidence;
- change current PASS/FAIL or acceptance state;
- approve a human gate;
- authorize worktree merge;
- authorize production release.

The payload declares these effects explicitly as `none`.

## Caller-injection defense

Both canonical memory keys are stripped before flow selection:

```text
prior_evaluation_insight
prior_quality_insight
```

They are also stripped from replanning context **after** applying caller `context_updates`, so a caller cannot re-inject historical memory as policy input.

Only the runtime may attach trusted project-scoped advisory memory after flow selection.

## Stage propagation

When present, bounded advisory memory may be copied into specialist stage context so providers can use it as a hint about where to inspect.

This propagation does not promote the memory into evidence and does not change the stage's tools, authority or gates.

## Failure behavior

Quality recall is fail-open and non-authoritative.

If the project memory is missing, disabled, corrupt, locked or unreadable:

- flow selection still uses the current task only;
- the run proceeds without quality recall;
- current-run evidence/gates remain authoritative;
- memory failure cannot turn a valid run into FAIL;
- memory failure cannot hide an existing current-run failure.

## Verification

Regression coverage must prove at least:

1. recalled quality insight is bounded and categorical;
2. raw prose/artifacts never re-enter provider context through A5.5;
3. repeated failures are ordered by observed occurrence count;
4. caller-supplied memory keys are absent during flow planning;
5. trusted quality insight is attached only after flow selection;
6. specialist stage context receives only the bounded advisory payload;
7. both memory channels are stripped from replanning context, including caller re-injection attempts;
8. `evaluation_memory.enabled = false` produces no quality recall.

## Trust model

```text
provider/model statement   = claim/context
current runtime observation = evidence
cross-run evaluation memory = advisory aggregate
post-render quality memory  = advisory aggregate
```

Historical memory can tell a provider **where to look**. Only current-run runtime evidence can prove **what is true now**.
