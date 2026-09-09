# Playwright rendered-evidence adapter

This adapter turns rendered routes into evidence consumable by the existing visual-quality and template-monotony graders.

It is optional because `skills_UIUX` does not impose a Node/browser dependency on every consumer.

## Safety default

This adapter is **read-only capture by default**. Treat browser automation as a real action surface:

- do not run mutating production journeys such as checkout, payment, delete, account changes or mass updates;
- mutating flows belong on staging/preview with explicit authority and seeded test data/credentials;
- redact credentials, tokens, cookies and PII before persisting logs/screenshots;
- third-party console/network noise should be classified, not silently treated as product failure;
- no visual baseline means regression status is `INCONCLUSIVE`/unverified, never a silent PASS.

These rules are adapted from reviewed ECC browser-QA and Anthropic webapp-testing patterns. Provenance: `vendor/agent-runtime-intelligence/SOURCE-LOCKS.md`.

## Install in an execution environment

```bash
npm install -D playwright
npx playwright install chromium
```

## Capture

Create a JSON config:

```json
{
  "baseUrl": "http://127.0.0.1:3000",
  "outputDir": ".uiux-evidence",
  "routes": [
    {"name": "home", "path": "/"},
    {"name": "about", "path": "/about"}
  ],
  "viewports": [
    {"name": "desktop", "width": 1440, "height": 900}
  ]
}
```

Then:

```bash
node integrations/playwright/capture.mjs capture.json
```

For each route/viewport the adapter writes:
- screenshot PNG;
- rendered HTML (`page.content()`);
- console error log;
- failed request log;
- a manifest referencing the HTML and screenshot artifacts.

## Reconnaissance before interaction

For dynamic apps, prefer:

```text
navigate
→ wait for rendered state
→ inspect screenshot/DOM
→ identify stable role/label/test-id selectors
→ act only within declared authority
```

Do not guess selectors from source when rendered state can differ materially.

## Evidence semantics

Rendered screenshot existence is evidence collection, not proof that visual quality passed; the pixels still require inspection/rubric evaluation.

Likewise:

```text
capture success ≠ interaction success
no console error ≠ UX success
axe/automated scan ≠ accessibility conformance
no baseline ≠ visual-regression PASS
```

When a capture fails repeatedly, stop blind retry and use the failure-diagnosis reference owned by `agent-evaluation-and-reliability`.
