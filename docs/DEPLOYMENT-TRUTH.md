# Deployment Truth Gate — A35

A green build or merged PR is not proof that production serves the intended commit. A35 adds a release-evidence gate that keeps product QA separate from deployment/provider state.

## Verified release contract

`DEPLOYED_VERIFIED` is emitted only when all of these are true:

1. product QA is already green;
2. an expected release/merge SHA is declared;
3. provider deployment metadata contains a source SHA matching that expected SHA;
4. the deployment status is ready/successful;
5. a production URL/alias exists;
6. the production route probe returns HTTP 2xx.

Anything weaker remains a narrower state such as `READY_BUT_NOT_DEPLOYED`, `PROVIDER_RATE_LIMITED`, `AUTH_BLOCKED`, `BUILD_FAILED`, `DEPLOY_FAILED` or `INFRA_UNAVAILABLE`.

## CLI

From `uiux-factory/qa`:

```bash
node scripts/deployment-truth.mjs \
  --expected-sha "$MERGE_SHA" \
  --deployment-sha "$PROVIDER_SHA" \
  --deployment-status READY \
  --production-url https://example.com \
  --provider vercel \
  --output artifacts/deployment-truth/deployment-truth.json
```

When `--production-url` is present and no explicit `--probe-status` is supplied, the gate performs a bounded HTTP probe itself. Tests can inject `--probe-status` to remain network-independent.

## GitHub-native reuse

`.github/workflows/deployment-truth-gate.yml` supports both manual dispatch and `workflow_call`. Downstream workflows receive `classification` and `verified` outputs and should not promote a release unless `verified == true`.

## Evidence boundary

The gate verifies only the metadata supplied to it plus its own production route observation. A caller claiming a provider-reported SHA must obtain that SHA from provider/API/deployment metadata rather than inventing it from the expected source commit. If provider metadata is unavailable, keep the state `READY_BUT_NOT_DEPLOYED` or `UNKNOWN` instead of manufacturing `DEPLOYED_VERIFIED`.
