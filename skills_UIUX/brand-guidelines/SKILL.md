---
name: brand-guidelines
description: |
  Xây dựng, áp dụng và kiểm soát brand guideline cho website dựa trên evidence thật: logo, color,
  typography, imagery, tone, shape language, motion và digital tokens. Dùng khi có official guideline,
  partial assets hoặc cần tạo PROPOSED BRAND GUIDELINE — LOGO-DERIVED với confidence rõ ràng.
globs:
  - "docs/brand-guidelines.md"
  - "**/*.css"
  - "**/tokens.*"
  - "**/theme.*"
---

# Brand Guidelines — Evidence-first

## Goal

Biến brand truth thành **digital rules có thể implement**, không biến logo/màu primary thành một visual theme cảm tính.

Core rule:

`official evidence → verified asset evidence → limited inference → proposed digital rule`

Không được đi ngược chuỗi này.

## 1. Brand source status — bắt buộc

Trước mọi brand decision, phân loại:

```text
A — OFFICIAL BRAND GUIDELINE AVAILABLE
B — PARTIAL OFFICIAL BRAND ASSETS AVAILABLE
C — LOGO AVAILABLE, NO BRAND GUIDELINE
D — NO RELIABLE BRAND ASSET
```

Evidence priority:

```text
Tier 1 — Official brand guideline / brand book / design system
Tier 2 — Official logo package / trademark / vector assets
Tier 3 — Official website / app / annual report / company profile
Tier 4 — Official campaign / signage / verified social
Tier 5 — Logo visual analysis
Tier 6 — Professional inference
```

### Hard rule

- A → guideline là source-of-truth; chỉ mở rộng phần digital còn thiếu với `PROPOSED_FOR_DIGITAL`.
- B → giữ nguyên phần verified; chỉ infer phần thiếu.
- C → **bắt buộc** tạo `PROPOSED BRAND GUIDELINE — LOGO-DERIVED`; không được ghi đơn giản `brand unknown` rồi tự chọn style.
- D → chỉ tạo `PROPOSED BRAND DIRECTION — LOW CONFIDENCE`; không được gọi là brand guideline chính thức.

## 2. Evidence labels

Mỗi material brand decision dùng một trong:

```text
OFFICIAL
VERIFIED_FROM_OFFICIAL_ASSET
INFERRED_FROM_LOGO
INFERRED_FROM_OFFICIAL_ASSETS
PROPOSED_FOR_DIGITAL
PROPOSED_FOR_ACCESSIBILITY
UNKNOWN
```

Không gọi màu/font/voice là official nếu không có evidence tương ứng.

## 3. Brand audit

Kiểm tra tối thiểu:

- logo files/variants;
- official colors nếu có;
- official typeface nếu có;
- current website/app typography;
- imagery/photography;
- iconography;
- annual report/company profile;
- campaign/signage;
- brand story/positioning/tone evidence;
- existing digital tokens/components.

Tạo ledger:

| Brand dimension | Finding | Source | Status | Confidence | Digital implication |
|---|---|---|---|---|---|

## 4. Logo-derived fallback protocol

Khi status = C:

### 4.1 Verify official logo

Ưu tiên `SVG > PDF/vector > EPS/AI > high-resolution PNG` từ first-party source.

### 4.2 Analyze only what logo can support

Có thể suy ra có kiểm soát:

- geometry;
- visual weight;
- symmetry/asymmetry;
- curves/corners;
- stroke characteristics;
- proportion/negative space;
- direction/movement;
- verified/extracted colors;
- potential shape/motif language.

Logo **không đủ** để khẳng định:

- mission/vision;
- target audience;
- positioning;
- customer promise;
- brand values;
- tone of voice;
- photography strategy.

Các phần đó phải đến từ business/first-party evidence hoặc giữ `UNKNOWN`.

### 4.3 Extract colors with provenance

| Color | HEX/RGB | Source | Status | Confidence | Intended role |
|---|---|---|---|---|---|

`logo color ≠ UI semantic color`.

Nếu logo color không đạt contrast cho action/text, giữ nguyên logo color và tạo companion color `PROPOSED_FOR_ACCESSIBILITY`; không âm thầm đổi màu logo.

### 4.4 Typography fallback

Không đoán exact font từ logo.

Ghi:

```text
Official Typeface: UNKNOWN
Logo Typography Signal: ...
Observed Website Typeface: ...
Proposed Digital Typeface: ...
Status: PROPOSED_FOR_DIGITAL
```

Font đề xuất phải xét locale/Vietnamese, readability, weights, licensing và performance.

## 5. Brand strategy boundary

Personality, positioning và tone chỉ được define khi có evidence đủ.

Không bắt buộc dùng archetype. Nếu archetype không có business evidence hoặc không giúp implementation, bỏ.

Tạo:

| Dimension | Evidence | Status | Design/copy implication |
|---|---|---|---|

## 6. Semantic color role map

Không chỉ tạo palette. Bắt buộc define role:

- brand primary / secondary;
- page background;
- surface / alternate surface / dark surface;
- text primary / secondary / muted / inverse;
- border/divider;
- primary action / hover / active / focus;
- link;
- brand accent/wayfinding;
- success/warning/error/info khi applicable.

Mỗi role phải có allowed usage + prohibited usage.

Brand primary không mặc định dùng cho mọi CTA, mọi heading và mọi section background.

## 7. Typography system

Define:

- heading/body family + evidence/status;
- display/H1/H2/H3/body/meta/action hierarchy;
- line-height/line-length;
- locale behavior;
- mobile transformation;
- fallback behavior.

Không dùng type scale mặc định như universal truth. Scale phải phù hợp content density, domain và actual layouts.

## 8. Logo usage + state matrix

Ngoài clear-space/min-size, bắt buộc kiểm các rendered contexts:

| Context | Logo variant | Background | Contrast/result |
|---|---|---|---|
| top nav | ... | ... | ... |
| scrolled nav | ... | ... | ... |
| mobile menu | ... | ... | ... |
| dark section/footer | ... | ... | ... |
| light section | ... | ... | ... |

White logo on white nav, dark logo on dark surface hoặc filter/invert không kiểm chứng là P0/P1 brand defect tùy mức ảnh hưởng.

## 9. Shape / layout / imagery / icon / motion language

Cross-check official assets trước khi proposal.

- Shape language có thể kế thừa geometry logo nhưng không biến mọi component thành logo shape.
- Imagery không được suy ra chỉ từ logo; phải audit actual brand photography/collateral.
- Icon style phải coherent với brand/domain và UI density.
- Motion chỉ lấy cue từ brand rhythm/direction khi có rationale; không làm logo distortion hoặc decorative overload.

## 10. Brand distinctiveness test

Trước khóa visual direction, hỏi:

> Nếu che logo + brand name, website còn có thể được nhận ra nhờ color roles, typography, imagery, composition, shape/motif hoặc motion không?

Nếu câu trả lời là “có thể thay logo bằng bất kỳ competitor nào”, brand-to-digital translation chưa đủ.

Không giải quyết bằng cách rải primary color nhiều hơn; phải quay lại evidence + domain + visual signature.

## 11. Output

Tạo `docs/brand-guidelines.md` hoặc equivalent gồm:

1. Brand source status.
2. Evidence ledger.
3. Official vs inferred vs proposed decisions.
4. Logo usage/state matrix.
5. Semantic color roles.
6. Typography.
7. Imagery/icon/shape/motion direction.
8. Brand signatures.
9. Do / Don't.
10. CSS/design tokens chỉ cho các quyết định đủ confidence.

Nếu status C, title phải ghi rõ:

`PROPOSED BRAND GUIDELINE — LOGO-DERIVED`

## 12. Acceptance criteria

- [ ] Brand source status A/B/C/D đã xác định.
- [ ] Không fabricate positioning/voice từ logo.
- [ ] Official/inferred/proposed được phân biệt.
- [ ] Logo color và UI semantic color không bị đánh đồng.
- [ ] Color roles có usage/prohibition.
- [ ] Typography có evidence/status + locale/mobile rules.
- [ ] Logo được kiểm trong light/dark/scrolled/mobile states.
- [ ] Imagery/icon direction trace được về evidence/domain.
- [ ] Có brand recognition test.
- [ ] Code tokens không claim official nếu chỉ là proposal.

## Anti-patterns

- “Không có guideline → tự tạo một brand mới” mà không label confidence.
- Gọi màu trích từ logo là official.
- Đoán exact font từ wordmark.
- Suy ra mission/voice/persona chỉ từ logo.
- Dùng primary color ở mọi nơi để tạo cảm giác branded.
- Brand doc một kiểu nhưng rendered UI một kiểu.
- Chỉ kiểm token, không kiểm logo/CTA trên actual background states.
