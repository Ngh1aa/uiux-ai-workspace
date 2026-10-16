---
name: html-to-figma-export
description: Audit and implement deterministic HTML-to-Figma capture routes using canonical product renderers, reproducible states, truthful manifests and rendered export QA.
---

# HTML to Figma Export

Use for explicitly requested HTML-to-Figma / html.to.design / dMaya capture surfaces.
This skill owns capture delivery, not Figma-native artifact quality or research validity.

## Research

1. Recover the agreed screen inventory; retain its names and order.
2. Audit the exact target SHA and identify each existing screen, interaction-only state, missing state, canonical route/query and owning component/runtime.
3. Read the target renderer/state/style and generation contracts before editing.
4. Record mutation and deploy authority separately. A project profile cannot authorize either.

## Design and implementation

- Reuse one canonical renderer and product-data/state owner. Prefer a wrapper or route registry over one independent implementation per capture.
- Extend missing states with existing composition families/components/tokens. Export-only fixtures must be explicit and simulated.
- Give every screen a deterministic, directly navigable URL. Pin loading, processing and modal states; prevent automatic navigation during capture.
- Isolate fixture storage without clearing or altering a visitor's existing prototype state. Asset paths must resolve at nested routes.
- Keep capture-specific behavior outside the production path. Respect generated-file ownership and verify regeneration.
- Publish one manifest with count/unique ID/name/path, expected public URL or unresolved-origin placeholder, viewport, canonical screen/state/fixture, source-audit status, render readiness and separate deployment/public-access state.
- Unknown capture IDs must fail visibly, never silently render Home.

## QA

- Enumerate every manifest URL and verify an intentional semantic state, visible DOM, errors, media and unintended redirects.
- Test representative responsive screens and critical native flows, including failure/recovery.
- Assert amount/reference/recipient continuity, disabled confirmation offline/insufficient, frozen versus restricted consequences, and truthful KYC/payment/authentication boundaries.
- Test polluted browser storage and repeated capture navigation; exports must remain deterministic and native storage must survive unchanged.
- Check converter/import fidelity on representative screens when available. If conversion has not run, say UNVERIFIED; HTML readiness is not Figma import PASS.

## Deployment and handoff

Use the configured host; branch preview is sufficient when main must remain unmerged.
Before claiming public readiness, retain provider status, deployment/source SHA, anonymous HTTP evidence and rendered route evidence. A login-protected preview is not a usable public converter URL.
Report local QA, exact-head CI, preview/production deployment and import quality independently.
Do not claim that a converter automatically creates semantic variables, reusable variants or prototype connections.

## Gates

- Inventory coverage and canonical source reuse.
- Deterministic state/asset/storage isolation.
- Rendered responsive and critical-flow evidence.
- Truthful public URL/expected URL and readiness separation.
- Explicit import-quality limitation when the converter/plugin was not verified.
