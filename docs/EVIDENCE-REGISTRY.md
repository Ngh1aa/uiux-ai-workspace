# Release Evidence Registry — A36

A36 creates one release-level manifest that points to real QA/deployment artifacts without replacing the existing detailed evidence-lineage system.

## Ownership

- `core/provenance/evidence_lineage.py` remains the owner for fine-grained evidence records and spec links.
- `core/provenance/release_evidence_registry.py` owns release-level artifact inventory, integrity hashes and cross-gate claim state.
- `skills_UIUX/scripts/build-release-evidence.py` is the CLI adapter.

## Manifest

The default output is `uiux-evidence-manifest.json` using schema `uiux-release-evidence.v1`.

Each artifact receives a stable `REL-...` ID, SHA-256 digest, byte size, kind and evidence state. Typical kinds include:

- `task_manifest`
- `state_coverage_report`
- `state_matrix`
- `responsive_screenshot`
- `browser_qa`
- `accessibility`
- `lighthouse`
- `deployment_truth`

The registry derives bounded claims for state coverage, browser artifacts, deployment truth and overall release readiness. Missing evidence stays `UNKNOWN`; it is never inferred into a pass.

## CLI

```bash
python -B skills_UIUX/scripts/build-release-evidence.py \
  --repository owner/project \
  --target-sha "$TARGET_SHA" \
  --artifact state_coverage_report=artifacts/state-coverage/state-coverage-report.json \
  --artifact state_matrix=artifacts/state-coverage/state-matrix-2x2.png \
  --artifact deployment_truth=artifacts/deployment-truth/deployment-truth.json \
  --output uiux-evidence-manifest.json
```

The registry cross-checks deployment truth `expected_sha` against the declared target SHA. A mismatch downgrades release classification instead of silently combining evidence from different revisions.
