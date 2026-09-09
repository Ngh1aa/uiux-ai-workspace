---
name: media-crop-and-layout-integrity
description: |
  Hard QA gate cho image crop, focal point, aspect-ratio và layout integrity trong website UI/UX.
  Dùng cho fashion/ecommerce/editorial hoặc bất kỳ redesign nào có media quan trọng để chặn ảnh mất đầu,
  crop sai chủ đích, card bị tách text khỏi ảnh, grid bị kéo thành lát dọc, hero overflow và layout drift.
---

# Media Crop & Layout Integrity

## Goal

Rendered UI phải giữ đúng chủ thể, tỷ lệ và quan hệ giữa media ↔ copy ↔ CTA ở mọi viewport.

`asset truth → intended focal point → container ratio → crop strategy → perceived subject scale → rendered screenshot → integrity review → PASS/FAIL`

## 1. Trigger

Bật bắt buộc khi:

- fashion / beauty / lifestyle / portfolio / ecommerce dùng photography;
- hero, campaign, editorial spread, product grid, PDP gallery;
- substantial visual redesign thay đổi aspect-ratio, object-fit hoặc media density;
- user phản hồi ảnh bị cắt đầu/mất chủ thể/lệch layout;
- các card cùng grid có model/product nhìn to nhỏ khác nhau dù container bằng nhau.

## 2. Asset truth before crop

Trước khi set `object-fit: cover`, inspect:

- source dimensions / orientation;
- subject type: full-body, half-body, product-only, detail, landscape;
- focal point: face/head, garment, product, hand/accessory, architectural subject;
- safe crop region;
- whether source has enough resolution for target container;
- **source framing / perceived scale**: subject chiếm bao nhiêu phần trăm frame so với các asset cùng component family.

Record when material:

| Asset | Source ratio | Subject/focal point | Intended container | Crop mode | object-position/focal token | Media scale | Mobile rule |
|---|---:|---|---|---|---|---:|---|

Không dùng `cover center` hoặc `contain` như default mù quáng.

## 3. Focal-point rule — HARD FAIL

Nếu ảnh có người và head/face là meaningful visual context:

- không cắt qua trán/mắt/cằm một cách ngẫu nhiên;
- không crop mất toàn bộ đầu khi source là portrait/fashion look trừ khi art direction cố ý và được contract ghi rõ;
- không tạo crop mà garment/product chính bị mất;
- không dùng một `object-position` cho mọi ảnh nếu focal point khác nhau.

Fashion product/card ưu tiên **garment silhouette + enough body context**. PDP main image ưu tiên xem sản phẩm đầy đủ hơn là dramatic crop.

## 4. Aspect-ratio integrity

Mỗi component family phải có ratio strategy rõ:

- product grid: ratio ổn định, không ép ảnh ngang thành portrait slice;
- editorial/campaign: có thể bất đối xứng nhưng crop phải preserve focal point;
- PDP main gallery: `contain` hoặc cover có safe focal strategy, không cắt thông tin sản phẩm;
- thumbnails: có thể cover nhưng phải vẫn nhận diện được ảnh;
- utility/content imagery: tránh cinematic crop nếu không phục vụ task.

HARD FAIL nếu rendered result tạo:

- vertical slivers / narrow slices;
- stretched/squashed subject;
- giant empty whitespace vì intrinsic ratio + fixed dimension conflict;
- image overflowing neighboring content;
- inconsistent image height làm text/card alignment vỡ vô lý.

## 4.1 Component-family crop consistency — HARD GATE

**Cùng ratio không đồng nghĩa cùng crop.** Với product grid, collection rail, related products, avatar/list card hoặc bất kỳ component family lặp lại nào, review cả **perceived subject scale**.

Ví dụ FAIL:

- 4 product cards đều 3:4 nhưng một model chỉ thấy từ ngực trở lên trong khi ba card còn lại thấy gần full-body;
- một ảnh có đầu lớn gấp ~1.5–2× các ảnh cạnh bên chỉ vì source đã crop chặt;
- `object-fit: contain` giúp không mất đầu nhưng tạo ra một asset nhìn phóng đại/lệch nhịp so với cả grid;
- cùng một sản phẩm ở Home/PLP/Related có perceived scale khác nhau không có rationale.

Required strategy:

1. chốt **canonical frame ratio** cho component family;
2. chốt **target subject scale** bằng screenshot của 3–6 card representative;
3. asset nào intrinsically tighter/looser phải dùng **asset-level focal/scale metadata** hoặc alternate source;
4. ưu tiên metadata/token, không hard-code ngẫu nhiên theo `nth-child`;
5. nếu source quá chặt và không thể normalize mà vẫn giữ garment/face → thay source ảnh;
6. hover animation không được làm phá normalized scale vừa chốt.

Allowed implementation pattern:

```css
.catalogue-media {
  aspect-ratio: 3 / 4;
  overflow: hidden;
}

.catalogue-media img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: var(--media-position, 50% 8%);
  transform: scale(var(--media-scale, 1));
  transform-origin: var(--media-origin, 50% 8%);
}
```

Asset/config example:

```text
product-a → media-scale: 1.00, media-position: 50% 8%
product-b (source crop chặt hơn) → media-scale: 0.82, media-position: 50% 6%
```

Các số phải đến từ rendered comparison, không đoán rồi bỏ đó.

### Page-role exception

Không ép một crop policy cho mọi page role:

- **PLP/Home product card / related rail:** ưu tiên visual consistency của merchandising set + nhận diện garment;
- **PDP main:** ưu tiên subject/product completeness, thường `contain` và không ép cùng perceived scale với PLP;
- **campaign/editorial:** art direction có thể khác nhưng phải có focal rationale;
- **thumbnail/transaction row:** có thể compact hơn nhưng vẫn không được mất subject vô lý.

Do đó rule đúng là **consistent within the same component family**, không phải “mọi ảnh toàn website phải dùng cùng object-fit/scale”.

## 5. Media ↔ text ownership

Card/listing phải nhìn như một đơn vị:

- image, product name, price, metadata, quick action cùng một visual owner;
- text không rơi sang column khác hoặc nằm cách xa ảnh do grid inheritance;
- CTA không tách khỏi sản phẩm mà nó điều khiển;
- price/name alignment không dựa vào accidental line-height/auto-placement.

Nếu card screenshot không thể nhìn ra text thuộc ảnh nào → P1 layout integrity failure.

## 6. Hero/layout bounds

Top-of-page phải kiểm:

- oversized type không bị viewport clip trừ khi art direction intentional và vẫn đọc được hierarchy;
- absolute-position text không đè/cắt navigation;
- first screen không có unexpected blank column/void;
- hero media không biến mất vì z-index/grid placement;
- content không nằm ngoài visual bounds ở 375/390/430/768/1440/1920 khi relevant.

## 7. Screenshot review — REQUIRED

Automated DOM metrics không đủ.

Cho mỗi representative media-heavy page, capture actual rendered screenshot và inspect visually:

### Desktop
- top viewport;
- at least one product/editorial section;
- full page when useful.

### Mobile
- first screen;
- product cards/listing;
- PDP image + purchase info;
- drawer/sticky state if relevant.

Review checklist:

- [ ] face/head intact when expected;
- [ ] garment/product identifiable and not accidentally cropped;
- [ ] **same component family có perceived subject scale nhất quán**;
- [ ] không có một card zoom chặt/lỏng bất thường so với hàng bên cạnh;
- [ ] no sliver/stretch;
- [ ] no accidental blank space;
- [ ] text belongs to the correct image/card;
- [ ] CTA belongs to the correct decision object;
- [ ] no overlap/clip at viewport edge;
- [ ] image hierarchy matches page role.

## 8. Crop variants / focal tokens

Prefer explicit component/data ownership, e.g.:

```css
.media {
  object-fit: contain;
  object-position: var(--focal-x, 50%) var(--focal-y, 50%);
  transform: scale(var(--media-scale, 1));
}
```

or data/config per asset:

```text
portrait-full-body → 50% 20%, scale 1.00
portrait-source-tight → 50% 8%, scale 0.82
portrait-face-led → 50% 12%, scale 1.00
product-flatlay → 50% 50%, scale 1.00
```

Values must come from rendered inspection, not guesswork alone.

## 9. Responsive crop rule

Desktop crop does not automatically transfer to mobile.

At pressure points, decide explicitly:

- `cover` vs `contain`;
- different object-position;
- different aspect-ratio;
- different `media-scale` when a smaller viewport changes perceived crop materially;
- alternate asset when necessary;
- whether composition should reflow around image rather than crop harder.

## 10. User-feedback regression

If user says:

- ảnh bị cắt đầu / mất mặt;
- crop lệch;
- một card crop/zoom khác hẳn các card còn lại;
- layout lệch;
- card text/image không ăn nhau;
- hình bị kéo thành lát dọc;

classify as **P1 PROCESS REGRESSION** when visually obvious.

Required response:

1. capture exact failing viewport;
2. identify CSS/component/data owner;
3. fix root cause;
4. add regression screenshot/assertion;
5. re-render same viewport;
6. inspect screenshot manually before release.

## 11. Release gate

Do not merge/deploy media-heavy redesign when any representative route has:

- obvious head/face/subject crop failure;
- **one merchandising card visibly zoomed/cropped out of family**;
- image sliver/stretch;
- product-card ownership ambiguity;
- hero overflow/clip;
- unexpected large blank region;
- layout alignment failure visible in screenshot.

Automated PASS cannot override obvious screenshot failure.

## Core principle

> **The browser screenshot is the truth. Matching aspect-ratios are not enough: repeated media must also match perceived crop and subject scale.**
