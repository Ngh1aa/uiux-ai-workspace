# Scripts

## Soát theo gu (`taste-check.cjs`)

Soát trang đã render theo [`TASTE.md`](../../../TASTE.md) trong Chromium, cả chế độ sáng và tối.
Mỗi phần tử có `data-screen="Tên màn"` được soát như một màn riêng.

- **Lỗi:** dấu " · " nối cụm từ, chữ dưới ngưỡng tương phản AA, nhãn ngắn bị gãy dòng, nội dung
  tràn ngang, hơn một card nổi bật trong một màn.
- **Cảnh báo:** card có nhiều bán kính bo góc, hơn 3 nhóm màu, vùng chạm dưới 44×44 px, chữ bị cắt
  bằng "…", dòng cuối chỉ còn một chữ.

```bash
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs design-system/starter/mobile.html \
  --width 390 --width 1280 --screenshot qa/
```

Tuỳ chọn: `--root` (thư mục phục vụ file, mặc định thư mục hiện tại), `--width` (lặp được),
`--height`, `--theme light|dark|both`, `--screenshot <thư mục>`, `--json <file>`. Thoát với mã 1
khi có lỗi. Cần Playwright (`npm install --no-save playwright` hoặc đặt `NODE_PATH`).
Test: `node --test skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.test.cjs`.

Script là tín hiệu tự động, không thay việc mở ảnh chụp ra nhìn.

## Elementary visual integrity runner

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
