# A4.6–A4.9 — Sandbox, Finalization, Release and Browser Evidence

This contract extends the canonical Flow OS runtime after A4.1–A4.5 hardening.

## A4.6 — OS / Container / Network Sandbox

Provider-facing `run_target_command` no longer executes target project code directly on the host.

The canonical runtime requires a locally available Docker or Podman engine and a pre-provisioned image for the command family.

Default sandbox invariants:

- exact argv only; no shell parsing;
- `--network none`;
- read-only container root filesystem;
- only the isolated Git worktree is mounted writable at `/workspace`;
- `--cap-drop ALL`;
- `no-new-privileges`;
- bounded PIDs, memory, CPUs, timeout and output;
- bounded tmpfs;
- no host secrets/environment forwarding;
- no implicit image pull;
- no fallback to host execution when the engine/image is unavailable.

The sandbox is a runtime boundary, not a claim that arbitrary container escapes are impossible. Keep Docker/Podman and the host OS patched and treat the project worktree as untrusted code.

## A4.7 — Worktree Finalize / Auto Merge / Cleanup

Writable managed work remains isolated on `uiux-agent/<run-id>`.

Finalization requires:

- the managed flow is `COMPLETED`;
- caller authority is at least `external_write`;
- source checkout is clean;
- source `HEAD` still equals the worktree base commit;
- source branch is named and unchanged during finalize.

Runtime finalization:

1. stages all worktree changes;
2. creates one runtime-managed commit with Git hooks disabled;
3. merges with `git merge --ff-only` only;
4. removes the linked worktree using `git worktree remove`;
5. deletes the merged `uiux-agent/<run-id>` branch;
6. prunes stale worktree metadata.

No force merge, conflict resolution, history rewrite or dirty-worktree force removal is performed automatically.

## A4.8 — Production Deploy Authority

Production deployment is intentionally outside model/provider roles.

Requirements:

- caller authority must be `release`;
- explicit confirmation must equal `PRODUCTION`;
- managed flow must be `COMPLETED`;
- any isolated worktree must already be finalized/merged;
- trusted evidence must contain no failing result;
- at least one `PASS` `browser_render` record must exist;
- at least one successful `validator_result` or `command_result` must exist.

The bundled generic deploy adapter reads one exact argv array from `UIUX_PRODUCTION_DEPLOY_ARGV_JSON`, executes with `shell=False`, and only forwards environment names allowlisted by `runtime-policy.json`. Secret values are never persisted into checkpoints/evidence.

For Vercel-style deployments the policy permits `VERCEL_TOKEN`, `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` names, but no credential values are stored in the repository.

Provider agents cannot acquire release authority through natural language and cannot call the production deploy controller as a model tool.

## A4.9 — Browser-Rendered Evidence Adapter

`PlaywrightBrowserEvidenceAdapter` bridges the existing real Playwright Cloud QA output into Flow OS typed evidence.

Each browser observation records:

- route and final URL;
- title and viewport;
- representative element bounding box;
- screenshot path and SHA-256;
- browser-evidence JSON SHA-256;
- bounded ARIA snapshot;
- console errors;
- page errors.

A browser record is `PASS` only when navigation produced a representative box and no page/console errors were observed. Otherwise it is `FAIL`.

Remote URLs are denied by default. Direct capture accepts localhost only unless `browser_evidence.allow_remote` is explicitly enabled by runtime policy.

Screenshots complement accessibility/ARIA snapshots: rendered pixels establish visual evidence while accessibility snapshots establish semantic structure.

## CLI examples

Ingest existing Playwright artifacts:

```bash
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../target-project \
  --managed-run-id <run-id> \
  --browser-artifacts uiux-factory/qa/artifacts
```

Finalize after the managed flow is complete:

```bash
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../target-project \
  --managed-run-id <run-id> \
  --authority external_write \
  --finalize-worktree \
  --commit-message "uiux-agent: finalize product work"
```

Production deploy after rendered evidence has been attached:

```bash
export UIUX_PRODUCTION_DEPLOY_ARGV_JSON='["vercel","--prod","--yes"]'
python -B skills_UIUX/scripts/uiux-agent.py \
  --project ../target-project \
  --managed-run-id <run-id> \
  --authority release \
  --deploy-production \
  --confirm-production-release PRODUCTION
```

No step above silently escalates authority.
