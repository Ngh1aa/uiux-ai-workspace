---
name: asset-media-and-art-direction
description: |
  Quản lý photography, illustration, icon, SVG, video và responsive media cho website.
  Dùng khi chọn/thay ảnh, xây visual asset system, tối ưu crop/format/loading hoặc cần bảo đảm
  media đúng brand, đúng ngữ cảnh, có quyền sử dụng và không phá performance/accessibility.
---

# Asset, Media & Art Direction

## Rule 1: Meaning before decoration

Ảnh phải có job: chứng minh, giải thích, tạo context, thể hiện sản phẩm/con người/không gian hoặc tạo brand mood. Không thêm stock image chỉ để lấp khoảng trống.

## Asset inventory

Tạo bảng:

| Asset | Purpose | Source/rights | Ratio | Desktop crop | Mobile crop | Alt/caption | Delivery |
|---|---|---|---|---|---|---|---|

## Photography direction

Định nghĩa nhất quán:

- Subject.
- Lighting/tone.
- Camera distance.
- Composition.
- Human presence.
- Background complexity.
- Color treatment.
- What to avoid.

Không mix corporate stock, cinematic 3D và casual phone photography nếu không có rationale.

## Responsive art direction

Hero/feature image cần safe zone và focal point. Mobile có thể cần crop/asset khác; đừng phụ thuộc hoàn toàn vào `object-fit: cover`.

### Human-subject / primary-focal hard gate

Khi hero/feature media có người, khuôn mặt, sản phẩm hoặc focal subject rõ:

1. Xác định **focal subject + no-cut zone** trước khi code crop.
2. Inspect actual rendered crop ở mọi declared target viewport/pressure point.
3. `object-fit: cover`, `object-position: center`, `20%`, `top`... chỉ là implementation candidate; không phải bằng chứng crop đúng.
4. Với primary human/focal media, `cover` là **unsafe by default** cho đến khi crop contract được verify.
5. Không cắt qua mắt, khuôn mặt, đỉnh đầu hoặc identifying feature chính nếu art direction không cố ý yêu cầu như vậy.
6. Kiểm cả overlay/panel/copy block có che subject không.
7. Nếu một source asset không sống được qua các ratio cần thiết, ưu tiên `contain`, đổi composition, `<picture>`, alternate crop/asset hoặc source-aware layout; không ép một crop universal.
8. Sau fix phải recapture và **mở ảnh kiểm bằng mắt**. Screenshot tồn tại nhưng chưa inspect không tính là evidence.

Primary hero crop làm mất face/head/focal subject là P1 visual defect; nếu làm mất nội dung quyết định chính có thể P0 và phải chặn handoff/release.

### Crop contract for regression

Nếu production/release vẫn dùng `cover` cho primary/feature media, project phải có traceable crop contract gồm:

```text
asset / media owner
focal subject
no-cut zone / safe area
target viewports + pressure widths
intended fit/position or responsive art direction
rendered evidence inspected
```

Khi tooling cho phép, expose contract bằng machine-readable metadata hoặc deterministic mapping để regression có thể phát hiện `cover` mới chưa được verify.

Default regression policy:

```text
primary/focal media + computed object-fit: cover + no verified crop contract
→ BLOCKED
```

Metadata không tự chứng minh crop đẹp; nó chỉ ngăn một `cover` ngẫu nhiên lọt qua mà không có owner/evidence.

## Icons

- Một icon family/style chính.
- Consistent stroke/fill/corner/optical size.
- Icon không thay label ở action khó hiểu.
- Decorative icon `aria-hidden`; meaningful icon có accessible name qua control/text.

## SVG

- Clean unnecessary metadata.
- Dùng currentColor khi phù hợp theme.
- Không inline SVG khổng lồ lặp lại nhiều lần.
- Logo giữ aspect ratio và clear space.

## Video

- Có poster.
- Không autoplay audio.
- Hero background video phải có fallback image và không cản readability.
- Caption/transcript khi content mang thông tin.
- Không để video nặng trở thành LCP mặc định nếu không cần.

## Delivery

Chọn format/size theo browser/framework project. Luôn khai báo dimensions hoặc reserve aspect ratio để tránh layout shift. Lazy-load media dưới fold khi phù hợp; critical/LCP asset xử lý riêng.

## Acceptance criteria

- [ ] Mỗi asset có purpose và source hợp lệ.
- [ ] Image style nhất quán với brand.
- [ ] Crop được kiểm ở mọi viewport nằm trong declared scope.
- [ ] Human/primary focal subject có safe zone và không bị crop vô lý.
- [ ] Primary/focal `cover` có verified crop contract hoặc đã đổi sang safer art direction.
- [ ] `object-fit/object-position` đã được verified trên actual render, không chỉ đọc source.
- [ ] Alt/caption đúng vai trò.
- [ ] Dimensions/aspect ratio reserve layout.
- [ ] Icon family không bị trộn tùy tiện.
- [ ] Video có fallback và không phá performance.
