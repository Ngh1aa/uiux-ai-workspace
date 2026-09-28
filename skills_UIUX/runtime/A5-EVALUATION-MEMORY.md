# A5.1–A5.3 — Evaluation + Learning Memory Foundation

Status: **CANONICAL RUNTIME CONTRACT**

A5 builds on the completed A4 runtime instead of creating another orchestration path.
Executable behavior lives in `uiux-factory`; `skills_UIUX` owns this policy/contract documentation and `runtime-policy.json`.

## Scope

A5.1–A5.3 introduce three bounded capabilities:

1. **Evidence-derived run evaluation** — terminal managed runs receive a structured outcome derived from trusted runtime evidence.
2. **Project-scoped evaluation memory** — eligible outcomes are retained locally in bounded, atomic storage.
3. **Advisory cross-run recall** — future runs may receive aggregate prior-run insight after canonical flow selection.

This is not autonomous long-term model memory and is not a new Development Manager.

## Executable ownership

```text
uiux-factory/core/evaluation/run_evaluator.py
uiux-factory/core/memory/evaluation_memory.py
uiux-factory/core/runtime/flow_os/managed.py
```

Declarative policy remains:

```text
skills_UIUX/runtime/runtime-policy.json
```

## A5.1 — Evidence-derived run evaluation

`RunEvaluator` reads the latest effective trusted evidence emitted by the canonical Flow OS runtime.

It does **not** use these as proof:

- provider summaries;
- provider evidence claims;
- prompts or chain-of-thought;
- arbitrary model prose;
- historical memory records.

A run evaluation contains bounded metadata such as:

- flow id/revision;
- terminal managed state;
- evidence-derived outcome;
- task signature fields;
- completed-stage and replan counts;
- effective evidence counts/types/statuses;
- stable failing evidence channels.

Current outcomes are:

```text
passed
failed
blocked
insufficient_evidence
incomplete
```

A `COMPLETED` lifecycle with no trusted runtime evidence is `insufficient_evidence`, not `passed`.

When a validator, command or browser channel fails and the same channel is later rerun successfully, the canonical A4 effective-evidence semantics apply: the latest same-channel result supersedes the older failure. Unrelated PASS evidence cannot hide a FAIL.

## A5.2 — Project-scoped evaluation memory

Eligible evaluation records are stored below the target project:

```text
.uiux-agent-runs/memory/evaluation-memory.json
```

Default policy:

```json
{
  "evaluation_memory": {
    "enabled": true,
    "max_records": 200,
    "max_recall_records": 20,
    "min_signature_matches": 1,
    "lock_timeout_seconds": 10,
    "lock_stale_seconds": 60
  }
}
```

Storage invariants:

- project-local only;
- bounded record count;
- schema-versioned records;
- atomic temporary-file + `os.replace` writes;
- cross-process transaction serialization through the existing `RunLock` primitive;
- deduplication by managed run id;
- symlink/path escape rejection;
- malformed/ineligible records are not promoted into recall.

Model-facing `WorkspaceFileTools` already blocks `.uiux-agent-runs`, so provider write tools cannot modify the memory store.

## Memory eligibility

A record is eligible only when all of the following are true:

- managed state is terminal: `COMPLETED`, `FAILED` or `BLOCKED`;
- at least one trusted effective runtime evidence record exists;
- outcome is `passed`, `failed` or `blocked`.

Non-terminal runs and evidenceless completions are not learned.

## Data minimization

The memory schema intentionally excludes:

- raw prompts;
- provider summaries;
- provider claims;
- tool stdout/stderr;
- page HTML/DOM dumps;
- source file contents;
- secrets, tokens and credentials;
- arbitrary historical prose.

Failure channels are reduced to bounded identifiers such as stage/evidence type/tool plus a safe discriminator (for example validator name, command executable or browser route path).

## A5.3 — Advisory recall

A new managed run follows this order:

```text
current task
→ GoalInterpreter
→ FlowPlanner
→ resolved flow
→ recall aggregate prior-run evaluation insight
→ attach advisory insight to managed/stage context
→ provider/tool execution
```

The order matters: memory is attached only **after** flow selection.

Recall returns aggregate fields only, including:

- sample size;
- pass rate;
- failed/blocked count;
- average replans;
- recurrent failure channels;
- observed evidence types.

Raw historical records are not injected into provider context.

## Authority boundary

Evaluation memory is explicitly **advisory only**.

It cannot:

- choose or change the canonical flow;
- raise or reduce authority;
- satisfy a current-run gate;
- count as current-run evidence;
- approve a human gate;
- trigger or authorize merge;
- trigger or authorize production deploy;
- override current source-of-truth evidence;
- enter the canonical replanning policy context.

`ManagedFlowController.replan()` strips `prior_evaluation_insight` before calling `FlowPlanner.replan()`, including any attempted override supplied through `context_updates`.

## Terminal lifecycle integration

Whenever a managed Flow OS checkpoint reaches:

```text
COMPLETED
FAILED
BLOCKED
```

`ManagedFlowController` refreshes the structured run evaluation. If it is memory-eligible, the evaluation is transactionally recorded in project memory.

The manager checkpoint stores the current `run_evaluation` and whether the memory record was accepted.

## Advisory failure behavior

Memory availability is never a correctness or authority prerequisite.

If recall or recording fails because the memory file is corrupt, locked, unavailable or unwritable:

- canonical flow selection still uses the current task only;
- the run continues without prior insight;
- terminal run state/evaluation is preserved;
- gates/release behavior is unchanged;
- a bounded `evaluation_memory_error` diagnostic is stored in the manager checkpoint;
- `evaluation_memory_recorded` is false when recording failed.

A memory subsystem failure must not turn an otherwise valid run into `FAILED`, and it must not hide the original failure of a run that was already terminal.

## Trust model

A5 preserves the A4 distinction:

```text
provider/model statement = claim/context
runtime observation      = evidence
cross-run memory          = advisory aggregate
```

Only current-run trusted runtime evidence can satisfy current-run gates.

## Known limitation

This foundation is local/project-scoped, not a distributed analytics database or organization-wide learning service. It provides deterministic bounded learning context for repeated work on one project without weakening A4 security/authority boundaries.

The richer Factory post-render evaluator and prototype acceptance contract remain independent evidence producers. Bridging those richer quality outputs into canonical run evaluation is a later A5 extension, not part of A5.1–A5.3.
