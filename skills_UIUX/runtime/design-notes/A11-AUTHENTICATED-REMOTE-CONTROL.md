# A11 — Authenticated Remote Factory Control Plane

A11 exposes a bounded remote-control surface over the canonical managed Flow OS without turning MCP into a remote shell.

## Default posture

Remote lifecycle operations are **disabled by default** in `runtime-policy.json`.

Enabling them requires all of:

```text
remote_control.enabled=true
UIUX_REMOTE_CONTROL_TOKEN=<operator secret>
UIUX_REMOTE_PROJECT_ROOTS_JSON=["/explicit/allowed/root"]
```

Every authenticated operation checks the supplied project root against the allowlist after path resolution. No project root is inferred from model text.

Network exposure additionally requires TLS/HTTPS at the MCP/API transport or gateway. The runtime does not claim that stdio MCP by itself provides TLS.

## Exposed lifecycle actions

The canonical MCP adapter exposes:

```text
remote_health
start_managed_run
managed_run_status
managed_run_artifacts
read_managed_artifact
submit_creative_directive
start_revision_run
cancel_managed_run
```

These delegate to `RemoteFactoryControlPlane`, which reconstructs the existing `ProviderNeutralAgentHarness` + `ManagedFlowController` for the allowlisted project.

There is no second Flow planner or lifecycle engine.

## Authority boundary

Remote starts are capped at:

```text
read_only
branch_write
```

A remote caller cannot request `external_write` or `release` through A11. The control plane does not expose:

- arbitrary shell execution;
- arbitrary filesystem reads;
- provider/model selection;
- merge;
- deployment;
- production release;
- repository deletion or payment actions.

Existing runtime authority, approval, evidence and release boundaries remain authoritative.

## Safe artifact access

Artifact listing comes only from artifacts recorded by specialist run checkpoints.

`read_managed_artifact` additionally requires the requested path to appear in that run-owned artifact list and re-reads it through canonical `SafeReader`. Character count is bounded by `remote_control.max_artifact_chars`.

This is not a generic remote file API.

## Creative directives and revision runs

`submit_creative_directive` writes a bounded JSON directive under:

```text
docs/uiux/remote-directives/<manager_run_id>.json
```

and records its project-relative path in the managed task context.

`start_revision_run` creates a **new** canonical managed run and records `revision_of=<prior manager run id>`. It does not mutate a completed historical Flow into a new revision epoch or silently carry provider authority forward.

## Cancellation

Remote cancellation maps to the existing terminal `BLOCKED` managed state and records `remote_cancelled=true`. It does not introduce a parallel lifecycle state that provider runners might accidentally ignore.

## Audit

Every authenticated lifecycle/read mutation appends bounded metadata to:

```text
.uiux-agent-runs/remote-control-audit.jsonl
```

Audit rows contain action/outcome/run metadata but never persist the supplied token or artifact/directive content.

## Security invariants

- authentication uses constant-time token comparison;
- no configured token => fail closed;
- no configured project roots => fail closed;
- wrong token => fail closed;
- project path outside allowlist => fail closed;
- remote release authority is unavailable;
- health output reports only booleans/counts and never token/root values;
- TLS is required for any network transport deployment and remains a deployment responsibility.

Regression coverage lives in `uiux-factory/tests/test_remote_control_plane_a11.py`.
