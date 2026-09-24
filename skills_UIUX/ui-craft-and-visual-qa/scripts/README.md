# Elementary visual integrity runner

`elementary-visual-integrity.mjs` is a reusable Playwright regression guard for the failure class covered by `../checklists/elementary-visual-sanity-gate.md`.

It checks, across configured routes and viewports:

- catastrophic computed foreground/background collapse on visible text outside variable-media contexts;
- semantic interactive elements in default/hover/focus states;
- large primary/feature media using `object-fit: cover` without an explicit verified crop contract;
- route/runtime/console failures;
- top-of-page screenshot generation for mandatory human inspection.

## Example

```bash
npm install --no-save playwright
npx playwright install chromium

VISUAL_SANITY_BASE_URL=http://127.0.0.1:4173 \
VISUAL_SANITY_ROUTES=/,/shop,/cart,/checkout \
VISUAL_SANITY_VIEWPORTS=1363x936,1100x900 \
VISUAL_SANITY_INIT_SCRIPT=./scripts/qa-seed-state.js \
node .claude/skills/ui-craft-and-visual-qa/scripts/elementary-visual-integrity.mjs
```

`VISUAL_SANITY_INIT_SCRIPT` is optional, but it is required when material controls only render after deterministic data/auth/error/selection state is established. The script is injected with Playwright `browserContext.addInitScript` before page code runs.

For an intentionally cropped focal asset, expose deterministic traceability on the image or nearest owning frame:

```html
<figure data-crop-verified="true" data-focal-subject="model face + full jacket">
  <img src="hero.jpg" alt="...">
</figure>
```

Those attributes only prove that a crop contract was explicitly declared. They do **not** prove the crop is visually correct; the generated screenshots still have to be opened and inspected at every declared target viewport/pressure point.

This runner is a regression signal, not a WCAG conformance test. A broken rendered screenshot overrides a green automated result.
