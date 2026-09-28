# A7 — Vision Evidence Boundary

A7 adds image/screenshot interpretation to the canonical Flow OS without granting a vision model execution authority.

## Trust model

The browser capture remains the source of trusted evidence:

```text
Playwright screenshot artifact
→ browser_render (trusted runtime evidence)
→ VisionEvidenceAdapter
→ vision_observation (advisory, trusted=false)
```

A `vision_observation` can help an implementation or QA agent decide where to inspect next, but it cannot:

- satisfy a gate;
- turn a failing browser/validator record into PASS;
- authorize merge, deploy or production release;
- become trusted merely because its source screenshot was trusted;
- replace DOM, accessibility, console, validator or browser evidence.

The distinction is deliberate: the screenshot file and its SHA-256 are runtime facts; a model's interpretation of those pixels is a claim about those facts.

## Artifact contract

`VisionEvidenceAdapter` accepts only a trusted runtime `browser_render` record and then re-validates its referenced artifact.

The image must:

- be artifact-relative and remain below the configured artifact root;
- be a regular non-symlink PNG, JPEG or WebP file;
- pass a file-signature check;
- stay below the configured byte limit;
- match `browser_render.data.screenshot_sha256` exactly.

Inline `data:` URLs and base64 image payloads are rejected. Observation records persist only bounded metadata such as artifact name, SHA-256 and byte size; image bytes are never copied into run evidence.

## Vision output contract

Analyzer output is intentionally small and strict:

```json
{
  "summary": "What is visibly notable",
  "findings": [
    {
      "category": "layout",
      "severity": "warning",
      "summary": "Primary action appears clipped",
      "detail": "Inspect the responsive container",
      "confidence": 0.82,
      "bbox": {"x": 0.8, "y": 0.1, "width": 0.15, "height": 0.08}
    }
  ]
}
```

Unknown fields fail closed. Text, finding count, confidence and normalized bounding boxes are bounded. Authority-bearing keys such as approval, gate, pass, merge, release, deploy or decision are rejected at any depth.

Every emitted observation is marked:

```text
advisory_only=true
authority_effect=none
gate_effect=none
merge_effect=none
release_effect=none
trusted=false
```

## Zero-cost default

A7 does not require a cloud vision provider. With no analyzer configured, Flow OS validates the screenshot artifact and emits a `NOT_RUN` advisory observation stating that vision analysis was skipped. This preserves the zero-cost path and, importantly, does not manufacture a positive visual judgment.

Analyzers declaring `cost_class=local` or `cost_class=zero_cost` are accepted by default. Other analyzers are denied unless runtime policy explicitly enables `vision_evidence.allow_external`.

Enabling an external analyzer only permits the call; it does not change the trust or authority of its observation.

## Gate invariant

`vision_observation` is intentionally absent from `TRUSTED_EVIDENCE_TYPES`. `gate_evidence_errors()` therefore cannot use it to satisfy `evidence_types`, even if a future analyzer labels its own result positively.

This invariant is covered by `uiux-factory/tests/test_vision_evidence_a7.py`.
