# State Coverage Infrastructure

UIUX Factory treats lifecycle states as a rendered product contract, not a screenshot checklist.

This infrastructure was hardened after cross-project dogfood showed that an HTTP-200 / no-console-error browser run can still be semantically wrong: a requested Empty or Loading route may silently render the Normal UI. The State Coverage Gate therefore requires state-specific evidence in addition to ordinary browser health.

## 1. State Coverage contract

A target project can add a small JSON file such as `uiux-state-coverage.json` using `uiux-factory/qa/state-coverage.schema.json`.

```json
{
  "schema_version": "1.0",
  "name": "Example product",
  "entry_route": "/recruiter-state-lab.html",
  "frame_selector": "#productFrame",
  "states": [
    {
      "id": "empty",
      "label": "Empty",
      "scope": "iframe",
      "query": { "state": "empty", "pin": 1 },
      "assertions": [
        { "type": "selector", "selector": "[data-state-evidence=\"empty\"]" },
        { "type": "text", "text": "No accounts are connected" }
      ],
      "focus": "[data-state-evidence=\"empty\"]"
    }
  ],
  "matrix": {
    "states": ["empty", "loading", "error", "edge"],
    "columns": 2,
    "viewport": "desktop-1440"
  }
}
```

Default viewports are `1440×1000`, `768×1024` and `390×844`. A contract can override them with 1–6 named viewports.

## 2. Semantic assertions

The gate supports three deterministic assertion types:

- `selector` — selector must exist and be visible by default; optional `count_at_least` and `visible=false` are supported;
- `text` — visible rendered text must contain the declared semantic text after whitespace normalization; matching is case-insensitive by default so CSS `text-transform` cannot create a false negative. Set `case_sensitive=true` when casing is itself part of the acceptance contract. An optional `selector` narrows the text assertion to one visible region;
- `attribute` — a selector attribute must `equals` or `contains` the declared value.

Every non-normal state must declare at least one semantic assertion. This prevents `?state=empty` from passing while rendering Normal UI.

A37 real-project dogfood caught an edge case here: CENNEXT visibly renders authored labels through CSS uppercase transformations. State Coverage verifies semantic content without confusing presentation casing with missing content, while still requiring the selected region to be visible.

## 3. Rendered gate and evidence

Run from `uiux-factory/qa` after the target is served:

```bash
QA_BASE_URL=http://127.0.0.1:4173 \
QA_ARTIFACTS_DIR=artifacts \
npm run test:state -- --contract /absolute/path/to/uiux-state-coverage.json
```

For every state × viewport the gate checks navigation response, state-specific semantic assertions, outer and owned-scope horizontal overflow, console errors, page errors and rendered screenshots.

The report is written to `artifacts/state-coverage/state-coverage-report.json`.

## 4. Automatic rendered matrix

When `matrix` is enabled, the gate screenshots each state's declared `focus` element only after semantic evidence passes, then composes a deterministic PNG with Sharp.

Default output:

```text
artifacts/state-coverage/state-matrix-2x2.png
```

This is suitable for review artifacts or copying into a case-study asset path. The matrix is evidence output; teams decide separately whether a QA workflow is allowed to commit generated assets to the target repository.

## 5. Infrastructure failure classification

`uiux-factory/qa/scripts/infra-failure-classifier.mjs` keeps product failure separate from provider/runtime failure.

Canonical classes:

- `PRODUCT_QA_FAILED`
- `PROVIDER_RATE_LIMITED`
- `AUTH_BLOCKED`
- `BUILD_FAILED`
- `DEPLOY_FAILED`
- `READY_BUT_NOT_DEPLOYED`
- `DEPLOYED_VERIFIED`
- `INFRA_UNAVAILABLE`
- `UNKNOWN_FAILURE`

Example:

```bash
node scripts/infra-failure-classifier.mjs \
  --source vercel \
  --status failure \
  --text "build-rate-limit / upgradeToPro"
```

returns `PROVIDER_RATE_LIMITED`, not `PRODUCT_QA_FAILED`. Conversely `UIUX_STATE_COVERAGE_FAILED` is product-quality blocking and must not be dismissed as infrastructure noise.

## 6. GitHub-native external-agent runner

`.github/workflows/external-agent-runner.yml` is the cloud entrypoint for collaborators that can access GitHub but cannot execute the Factory locally.

It can be started from Actions or reused with `workflow_call`. It:

1. checks out Factory and the declared target repository/ref;
2. compiles the natural-language task into the canonical external-task manifest;
3. records the exact target SHA and a bounded source snapshot;
4. emits `external-task-manifest.json`, `github-external-agent-run.json` and `HANDOFF.md`;
5. optionally serves the target and runs the State Coverage Gate when `state_contract` is declared;
6. uploads the task packet and rendered QA evidence as GitHub artifacts.

The runner deliberately **does not invoke an LLM provider**. It is the governed GitHub-native control plane around an external AI collaborator, not a fake autonomous-agent claim. The collaborator still performs target implementation within the granted authority.

Private cross-repository checkout requires a compatible `UIUX_TARGET_REPO_TOKEN`. Public repositories can use the normal GitHub token where permissions allow.

## 7. Cloud QA integration

`Cloud QA Toolchain` now accepts optional `state_contract`. External targets without one keep the previous browser/a11y/performance/media behavior. Internal Factory smoke runs always exercise the fixture State Coverage contract so regressions in semantic assertions or matrix generation fail the toolchain itself.

## Completion rule

A lifecycle-state task is not complete merely because the route returns 200 or a screenshot exists. Required states must render their declared semantic evidence at the declared viewports, the gate must pass, and the final human/creative review remains separate from automated proof.
