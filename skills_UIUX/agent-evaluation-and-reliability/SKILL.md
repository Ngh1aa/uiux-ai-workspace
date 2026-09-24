---
name: agent-evaluation-and-reliability
description: Designs and interprets multi-trial evaluations for UI/UX coding agents using explicit tasks, stable environments, deterministic/model/human graders, capability/regression suites and reliability metrics. Use when validating whether agent behavior is consistently good rather than occasionally successful, or when repeated agent failures need evidence-backed diagnosis before retry.
---

# Agent Evaluation & Reliability

## Principle
One good run demonstrates possibility, not reliability.

Use the repository eval suite and provider-neutral result contract in [../evals/README.md](../evals/README.md).

## Core concepts
- **task** — prompt/environment/success criteria;
- **trial** — one independent attempt;
- **grader** — deterministic, model-based or human evaluation;
- **trace** — tool/output/environment record useful for diagnosis;
- **capability eval** — tests frontier quality;
- **regression eval** — protects known-good behavior.

## Workflow
### 1. Write unambiguous tasks
Two competent reviewers should be able to understand what success means. Avoid hidden assumptions in the grader.

### 2. Prefer outcome graders
For coding work prioritize build/tests/state/render outcomes. Use trajectory/tool-call checks only when the path itself is a requirement.

### 3. Mix grader types
- deterministic for build, file/state, lint, accessibility checks and contracts;
- model/rubric for visual/UX judgment;
- human calibration for high-value subjective criteria.

### 4. Run independent trials
Start each trial from a clean comparable environment. Avoid leaked state/history.

### 5. Report reliability honestly
Track raw success rate and score distribution. `pass@k` and `pass^k` are probability concepts; if estimated from observed trials, label them as estimates and state `k`/sample size.

### 6. Promote stable capability cases
When a capability becomes consistently reliable, move representative cases into regression coverage.

## Failure diagnosis routing

If the question is not “how reliable is this capability?” but “why is this agent run repeatedly failing/looping/drifting?”, load [Failure diagnosis & recovery](references/failure-diagnosis-and-recovery.md).

Use that reference only when there is an actual failure signal such as repeated tool calls, stale state, context drift, environment mismatch or retries without progress. Do not load it for an ordinary first-attempt implementation or a single deterministic compiler/test error that a narrower debugging owner already explains.

A recovered failure should feed back into the eval system when it reveals a stable capability/regression case. Recovery evidence is not itself proof of general reliability.

## Skill-change benchmarking

When `skill-authoring-and-governance` materially changes a skill's behavior, prefer comparable runs:

```text
new skill vs old skill
or
with skill vs without skill
```

Measure outcome first, then time/token/context/tool-call trade-offs. Do not reward a skill merely for causing more tool calls or a more elaborate trajectory.

## Gate
Do not claim `reliable` from one trial. Do not tune graders to reward a preferred tool choreography when multiple valid solutions exist.

## Anti-patterns
- One-shot benchmark declared complete.
- Grader expects an undocumented filepath/implementation.
- LLM judge without calibration or an `unknown/insufficient evidence` escape.
- Shared dirty environment across trials.
- Agent can pass by gaming the grader without solving the user task.
- Blind-retry loops treated as “more trials” without resetting/diagnosing the failure state.
