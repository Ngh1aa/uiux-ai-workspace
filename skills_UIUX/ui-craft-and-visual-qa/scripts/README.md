# Scripts

## Soát theo gu (`taste-check.cjs`)

Soát trang đã render theo [`TASTE.md`](../../../TASTE.md) trong Chromium, cả chế độ sáng và tối.
Mỗi phần tử có `data-screen="Tên màn"` được soát như một màn riêng.

- **Lỗi:** dấu " · " nối cụm từ, chữ dưới ngưỡng tương phản AA, nhãn ngắn bị gãy dòng, nội dung
  tràn ngang hoặc bị khung cha cắt mất, hơn một card nổi bật trong một màn, ảnh/font/CSS tải lỗi,
  vi phạm axe-core mức serious/critical (khi có cài axe-core), tràn ngang ở 320 px (với `--reflow`).
- **Cảnh báo:** card có nhiều bán kính bo góc, hơn 3 nhóm màu, vùng chạm dưới 44×44 px, chữ bị cắt
  bằng "…", dòng cuối chỉ còn một chữ, chữ sát mép màn hẹp.

```bash
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs design-system/starter/mobile.html --screenshot qa/
```

Mặc định soát ở 390 px và 1280 px. Ghi `--width` là thay mặc định; website nên dùng
`--width 390 --width 768 --width 1280 --width 1440 --reflow`. `--reflow` thêm một lượt ở 320 px
(tương đương phóng to 400%, WCAG 1.4.10), chỉ bắt tràn ngang; không dùng cho trang có khung điện
thoại cố định. axe-core chạy khi tìm thấy (`npm install axe-core@4` cùng chỗ với Playwright),
`--no-axe` để tắt; kết quả luôn ghi axe đã chạy hay chưa.

Tuỳ chọn: `--root` (thư mục phục vụ file, mặc định thư mục hiện tại), `--width` (lặp được),
`--height`, `--theme light|dark|both`, `--screenshot <thư mục>`, `--json <file>`. Thoát với mã 1
khi có lỗi, mã 2 khi không chạy được. Cần Playwright: script tự tìm qua `NODE_PATH`, `node_modules`
gần đó và thư mục npm toàn cục; không thấy thì in cách xử lý (xem thêm mục "Khi không chạy được
taste-check" trong [`START-HERE.md`](../../../START-HERE.md)).
Test: `node --test skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.test.cjs`.

Script là tín hiệu tự động, không thay việc mở ảnh chụp ra nhìn.

## Soát tĩnh khi không có trình duyệt (`static-check.cjs`)

Chỉ cần Node, không cài gì. Đọc mã nguồn trang và CSS cục bộ nó nạp, bắt những lỗi thấy được mà
không cần render: dấu " · " nối cụm từ, thiếu `lang`/viewport/`title`, viewport chặn phóng to, ảnh
thiếu `alt`, nút hoặc liên kết không có tên, chữ "Lorem ipsum"; cảnh báo màu viết cứng ngoài token,
`transition: all`, bỏ outline mà không có `:focus-visible`, chữ dưới 12px, emoji làm icon.

```bash
node skills_UIUX/ui-craft-and-visual-qa/scripts/static-check.cjs <trang.html>
```

Không đo được tương phản thật, tràn chữ hay gãy dòng, nên không thay được taste-check.
Test: `node --test skills_UIUX/ui-craft-and-visual-qa/scripts/static-check.test.cjs`.

## Soát lớp thương hiệu (`design-system/scripts/check-brand.py`)

Soát `brand.css` của dự án chồng lên design system: mọi cặp chữ/nền ở chế độ sáng và tối, hai khối
tối có giống nhau không, tên token có gõ nhầm không. Chỉ cần Python.

```bash
python3 design-system/scripts/check-brand.py <dự-án>/brand.css
```

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
