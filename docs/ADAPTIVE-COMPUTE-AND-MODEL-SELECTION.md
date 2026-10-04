# Adaptive Compute & External Model Selection

Status: **advisory-only / quality-preserving**

UIUX Factory can route internal provider calls, but an external ChatGPT/Codex collaborator normally chooses its model in the product UI **before** the execution prompt is sent. The Factory therefore must not pretend it can switch that consumer model mid-run.

This upgrade adds a deterministic **Execution Advisor** for external collaborators:

```text
task + target truth
        ↓
Task Contract / Flow OS
        ↓
Execution Advisor
        ├─ capability floor
        ├─ reasoning-effort recommendation
        ├─ progressive context plan
        ├─ stage/tool-loop model stickiness
        ├─ checkpoint/resume guidance
        └─ quality-parity measurement rule
        ↓
human selects model in the consumer UI
        ↓
external collaborator executes the governed Flow
```

## Design goal

The goal is not “use the cheapest model”.

The goal is:

> **Maximize verified task completion per available compute without reducing output quality.**

The repository's standing optimization order remains authoritative:

```text
Correctness → Grounding → Completion → Verification → Maintainability → Clarity → Compute efficiency
```

A token/cost optimization is rejected when it lowers the required capability floor, hides uncertainty, weakens verification, increases repair loops, or causes representative-task quality to regress.

## What was adapted

The implementation borrows **patterns**, not runtime dependencies or source code, from several model-routing/token-efficiency projects:

- RouteLLM-style strong/weak thresholding informed the deterministic capability floor.
- LiteLLM-style budgeting/usage visibility informed the measurement contract; the Factory already owns provider budgets and usage telemetry.
- LLMRouter-style strategy diversity is treated as future benchmark inspiration, not as a second routing runtime.
- Portkey-style gateway guardrails/caching/reliability reinforce the existing policy-owned provider boundary.
- Manifest/CortexPrism-style cascade concepts are deliberately advisory for external consumer UIs; no hidden paid fallback or automatic model escalation is introduced.
- SAAR-style session awareness informed the **model stickiness** rule: avoid switching model inside an active tool loop; reselect only at a clean stage/checkpoint.
- Frugon-style “measure before optimizing” informed the quality-parity promotion rule.
- Prompt caching informed stable-prefix/dynamic-tail context ordering. A cache hit is never assumed or used as evidence.
- Context-engineering guidance informed progressive disclosure: load the smallest high-signal context that is safe for the active decision.
- LLMLingua-style lossy prompt compression is **not enabled by default**. Mandatory rules, authority, acceptance criteria and unresolved failures must never be compressed away.

No new external package is required by this upgrade.

## External preflight

Before selecting a model in ChatGPT/Codex:

```bash
python -B skills_UIUX/scripts/advise-external-task.py \
  --repository owner/repo \
  --task "Review provider truth, read-only permissions and regression risk"
```

The output contains:

- `recommended_capability`: `efficient | balanced | advanced`;
- `capability_floor`;
- `reasoning_effort`: `low | medium | high`;
- whether a cheaper profile is allowed;
- why the recommendation was made;
- whether the task should be split into separate runs;
- context and checkpoint guidance.

The labels are intentionally provider-neutral so the repository does not become stale when product model names change.

## Manual-selection boundary

For external consumer UIs:

```text
Execution Advisor recommendation
        ≠ automatic model switch
        ≠ provider selection authority
        ≠ paid-provider consent
```

The human still selects the actual model. If a run is split, the model may be reselected between separate runs or at a clean checkpoint. It should not be switched mid tool-loop merely to reduce cost, because that can discard useful session/cache locality and complicate reasoning continuity.

Internal managed-provider routing remains owned by the existing Flow OS provider-routing policy. This upgrade does not create a second provider router.

## Context efficiency

The advisor preserves the existing progressive-disclosure rule:

```text
stable policy / authority / task contract / resolved flow
        ↓
active-stage routed skills
        ↓
target files needed by the current decision
        ↓
current-run evidence
```

Avoid by default:

- every skill at once;
- every historical A-series document;
- unrelated project files;
- repeated evidence already captured in a verified checkpoint.

Stable instructions should stay before dynamic evidence when practical so platform/provider prompt caching can help. The system never assumes that caching occurred.

## Quota exhaustion and resume

Long tasks should preserve state at stage boundaries. If quota is exhausted:

1. keep completed-stage status and evidence references;
2. record unresolved blockers/acceptance criteria;
3. resume from the latest verified checkpoint;
4. do not replay already verified work merely to reconstruct context.

This improves completion reliability without weakening the quality floor.

## Promotion rule for cheaper profiles

Do not make a cheaper profile the default because it “seems fine”.

Benchmark representative tasks and compare at minimum:

- acceptance-criteria completion;
- verification pass/fail;
- repair/retry count;
- completion before quota exhaustion;
- input/output token usage when transport metadata exists;
- elapsed time/cost when available.

Only promote a cheaper profile when quality is non-inferior and completion reliability does not regress.

## Non-authority boundary

Execution Advice is advisory data only. It cannot:

- grant or increase authority;
- choose a paid provider without explicit opt-in;
- satisfy gates;
- become runtime/browser evidence;
- authorize merge/deploy/release;
- override target-project truth or Flow OS routing.
