# A9 — Model-readable Browser Observation

A9 gives provider reasoning a bounded read-only browser observation tool without transferring BrowserQA acceptance authority to the model.

## Execution path

```text
provider
  ↓ browser_observe(base_url, route)
fixed Playwright capture
  ↓
canonical browser evidence artifacts
  ↓
bounded observation sanitizer
  ↓
provider observation context
```

The provider cannot supply JavaScript, CSS selectors, browser expressions or arbitrary browser-side code. It supplies only a base URL and one same-origin relative route. The existing `PlaywrightBrowserEvidenceAdapter` still owns URL/route validation, localhost-only defaults, cross-origin request blocking and artifact validation.

## What the model can observe

A9 exposes bounded facts useful for diagnosis:

- route, final URL, title and viewport;
- target bounding box and selected computed styles;
- bounded DOM excerpt + SHA-256;
- bounded accessibility-tree snapshot + SHA-256;
- a bounded set of semantic/interactive elements;
- element roles/text/ARIA state and bounding boxes;
- selected style properties;
- image intrinsic/rendered dimensions;
- console messages and errors;
- page errors;
- failed requests;
- blocked cross-origin requests;
- screenshot filename + trusted capture hash.

Screenshot bytes are not embedded in the provider observation.

## Acceptance ownership

The observation returned by `browser_observe` is marked:

```text
advisory_only=true
trusted=false
authority_effect=none
gate_effect=none
evidence_effect=none
```

`evidence_from_tool()` persists a small `browser_observation` record containing route/hash/count metadata only. DOM, ARIA and element bodies are deliberately omitted from the checkpoint evidence record.

`browser_observation` is not part of `TRUSTED_EVIDENCE_TYPES`, so it cannot satisfy a gate.

The deterministic path remains:

```text
PlaywrightBrowserEvidenceAdapter
→ browser_render (trusted runtime evidence)
→ gate/release evaluation
```

A provider may use A9 to decide what to inspect or repair, but it cannot turn its own observation into acceptance proof.

## Failed network requests

A9 also strengthens canonical browser acceptance evidence. The fixed Playwright capture records `requestfailed` events, and `browser_render` now fails when such requests exist.

This means richer model visibility does not weaken the deterministic gate; BrowserQA becomes stricter at the same time.

## Runtime policy

```json
{
  "browser_observation": {
    "enabled": true,
    "max_dom_chars": 12000,
    "max_aria_chars": 12000,
    "max_console_items": 40,
    "max_network_items": 40,
    "max_elements": 24
  }
}
```

Types and bounds fail closed. Remote target policy is inherited from `browser_evidence.allow_remote`, which remains `false` by default.

## Regression coverage

`uiux-factory/tests/test_browser_observation_a9.py` proves:

- DOM/ARIA/element observations are bounded;
- useful browser facts and screenshot hashes are exposed;
- failed network requests fail trusted `browser_render` evidence;
- persisted browser observation metadata strips large content;
- browser observations cannot satisfy gates;
- the tool is read-only/read-authority;
- malformed observation policy and missing routes fail closed.
