# UIUX Factory v1 — Quickstart

This is the canonical operator path for UI/UX work after A20. Keep the goal short; let
Factory resolve scope, Flow, specialist skills, evidence gates and replanning from the
repository instead of pasting a giant meta-prompt.

## 1. Choose the entrypoint

Use `run.py` when you want the Factory creative/product pipeline to create its normal run
artifacts:

```bash
cd uiux-factory
python run.py "Improve the existing onboarding without reopening unrelated product strategy."
```

Use the provider-neutral autonomous Flow OS when an agent should inspect a real Git
project, make bounded branch-scoped changes and run its canonical QA stages:

```bash
cd uiux-factory
python scripts/run_autonomous_flow.py \
  --project-root /absolute/path/to/project \
  --goal "Improve the existing onboarding without redesigning the whole product." \
  --source README.md
```

`--provider auto` is the default and only uses provider configuration allowed by
`skills_UIUX/runtime/runtime-policy.json`. Provider output is never treated as gate
evidence by itself.

## 2. Write a small goal, not a giant prompt

Recommended shape:

> Improve `<target>` for `<users>`. Preserve `<constraints>`. Success means `<observable outcome>`.

Useful scope words such as `component`, `section`, `page`, `whole website`, and
`whole product` help the canonical `GoalInterpreter` choose the adaptive change surface.
Do not copy a full Factory workflow into the prompt; Flow owns stage order and routing.

## 3. Understand the autonomous lifecycle

The v1 lifecycle is exposed as:

`prompt → audit → plan → execute → QA`

- **audit**: bounded repository/source-truth discovery;
- **plan**: canonical GoalInterpreter + declarative Flow selection;
- **execute**: provider→tool work under Flow authority in an isolated Git worktree;
- **QA**: the Flow's own typed evidence gates and rendered/browser gates where required.

An adaptive flow may combine concerns into fewer internal stages. `COMPLETED` means the
canonical managed run reached its gates; it does **not** mean merge, deploy, production
release, human aesthetic approval, or measured user outcome.

## 4. Resume without starting over

Every autonomous result prints `manager_run_id` and `recovery_snapshot`.

```bash
python scripts/run_autonomous_flow.py \
  --project-root /absolute/path/to/project \
  --resume-run-id <manager_run_id>
```

READY/RUNNING same-revision work resumes from its checkpoint. Terminal FAILED/BLOCKED
stages are never silently retried.

## 5. Explicit recovery after a failed write attempt

Use the snapshot label returned by the earlier run:

```bash
python scripts/run_autonomous_flow.py \
  --project-root /absolute/path/to/project \
  --resume-run-id <manager_run_id> \
  --recover-snapshot <snapshot_label>
```

Recovery first discards the **validated isolated worktree** if one is recorded, then
restores the hash-verified local checkpoint. It never rewinds the source branch and never
merges or deploys.

## 6. Inspect before integration

The result JSON contains:

- `flow_id` / `flow_revision`;
- `completed_stages`;
- `workspace` metadata for any isolated write worktree;
- `recovery_snapshot`;
- provider/model provenance;
- a `truth_boundary`.

Checkpoints live below `.uiux-agent-runs/` in the target project. Provider-facing writes
live in the canonical isolated Git worktree. Source integration remains a separate,
explicit operator action.

## 7. v1 done definition

A task is not "done" because a model says so. For an autonomous run, use the managed
state and evidence:

- `COMPLETED`: all applicable canonical stages/gates completed;
- `AWAITING_APPROVAL`: a human gate owns the next decision;
- `BLOCKED` / `FAILED`: stop, inspect evidence, then explicitly replan or recover;
- `DRY_RUN`: never counts as gate completion.

For the Factory release itself, `.github/workflows/a20-release-candidate.yml` is the v1
release gate. It runs the full test suite, runtime/Flow validators, benchmark v2
validation, the A20 structural/security audit and pinned cross-project dogfood.

## Non-negotiable safety/truth boundaries

- no implicit authority escalation;
- no automatic production release;
- no provider prose promoted to evidence;
- writable agent work uses isolated Git worktrees;
- target commands require the configured network-disabled container sandbox;
- remote browser targets remain disabled by default;
- human/aesthetic/user-outcome claims stay pending until real evidence exists.
