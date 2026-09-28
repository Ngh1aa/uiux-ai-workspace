# A4.2–A4.5 Runtime Hardening

Status: active canonical runtime contracts.

Canonical executable owner: `uiux-factory/core/runtime/flow_os/`.
Declarative policy owner: `skills_UIUX/runtime/runtime-policy.json`.

## A4.2 — Worktree Isolation

Provider-facing writes never target the source checkout directly. The first writable action creates a branch-scoped Git worktree under the canonical worktree root and records:

- source root;
- isolated workspace root;
- isolated branch;
- base commit;
- managed run ID.

Subsequent provider reads/writes use that worktree. Workspace metadata loaded from checkpoints is revalidated against the active harness and canonical worktree path before use.

Writable isolation is fail-closed: the target must be a real Git repository and the configured project root must equal the Git top-level directory. The runtime does not silently fall back to direct source writes or an untracked copy.

## A4.3 — Target Runner

`run_target_command` accepts argv arrays only. It does not use shell interpretation, pipes, redirection or command strings.

Commands must match `target_runner.commands` in `runtime-policy.json`. Execution is further bounded by:

- isolated worktree cwd;
- workspace-relative cwd validation;
- timeout cap;
- output cap;
- filtered environment allowlist;
- `CI=1` and an isolation marker.

This is **process-policy isolation**, not an OS/container/network sandbox. Allowlisted project tests/builds can execute project code and therefore must not be described as host or network isolation.

## A4.4 — Typed Evidence and Gates

Runtime tool observations are converted to typed evidence records such as:

- `file_read`;
- `file_change`;
- `search_result`;
- `command_result`;
- `validator_result`;
- `artifact`;
- `tool_observation`.

Trusted evidence must have `origin=runtime` and a recognized evidence type. Provider-supplied evidence prose is retained as `provider_claim` trace data with `trusted=false`; it never satisfies a runtime gate.

A gate may declare exact `evidence_types`. Provider-driven legacy gates without an explicit type list still require trusted runtime evidence appropriate to the active specialist role before PASS can advance the managed flow.

Dry-run execution never satisfies evidence gates.

## A4.5 — Better File Tools

Provider-facing file operations now include bounded:

- `search_text`;
- `list_files_recursive`;
- `replace_text`;
- `write_project_file`;
- existing Safe Read tools.

All write/replace operations are workspace-relative, reject root escape and symlink paths, block credential-bearing/generated/internal targets, cap write size and use atomic replacement. Write observations include hashes so downstream evidence can identify before/after state without treating model prose as proof.

Search/list operations are recursively bounded by file/match limits and inherit A4.1 secret/symlink/text filtering.

## Authority boundary

These stages do not expand authority:

- read/search/list remain `read_only`;
- write/replace/target-command operations require `branch_write`;
- release remains a separate critical authority boundary.

No A4.2–A4.5 feature grants direct filesystem, arbitrary shell, merge, deploy or production authority.
