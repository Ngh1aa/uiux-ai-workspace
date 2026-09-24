---
name: reference-analysis-and-design-to-code
description: |
  Phân tích Figma, screenshot, website reference hoặc visual mẫu rồi chuyển thành design rules,
  components và code responsive. Dùng khi user yêu cầu làm giống reference, screenshot-to-code,
  Figma-to-code hoặc học style từ website khác nhưng vẫn phải tạo output nguyên bản và maintainable.
---

# Reference Analysis & Design-to-Code

## Principle

**Extract rules, not pixels blindly.** Học layout logic, hierarchy và interaction; không sao chép logo, ảnh, text, proprietary assets hay distinctive composition một cách máy móc.

## Workflow

### 1. Decompose reference

Tách thành:

- Grid/container/breakpoints.
- Spacing rhythm.
- Type scale và line length.
- Color roles, không chỉ hex.
- Surface/radius/shadow/border rules.
- Component inventory.
- Image ratios/crop/safe zone.
- Motion/interaction patterns.
- Responsive transformations.

### 2. Distinguish three layers

1. **Brand-specific**: không copy nếu không thuộc project.
2. **Pattern-level**: có thể học (split hero, sticky filters, editorial grid...).
3. **Implementation detail**: chọn cách phù hợp stack hiện tại, không clone DOM/CSS vô lý.

### 3. Create inferred design spec

Trước code, ghi `docs/reference-to-design.md`:

| Rule | Reference evidence | Adaptation for project |
|---|---|---|

Nếu thiếu mobile reference, infer bằng priority: content → interaction → layout → decoration.

### 4. Map to existing system

- Reuse existing token/component nếu đủ.
- Extend variant trước khi tạo component mới.
- Không tạo `Hero2`, `CardNew`, `SectionFinal` chỉ để match screenshot.
- New token phải có semantic purpose.

### 5. Implement state-first

Với component interactive, code default/hover/focus/active/disabled/loading/error/empty trước khi polish animation.

### 6. Fidelity QA

So sánh theo thứ tự:

1. Structure và hierarchy.
2. Dimensions/spacing/alignment.
3. Typography.
4. Color/surface.
5. Imagery/crop.
6. Interaction/motion.

Không “fix” bằng hàng loạt magic numbers nếu root cause là grid/token sai.

## Responsive inference rules

- Không scale desktop xuống mobile theo tỉ lệ.
- Preserve reading order và primary CTA.
- Chuyển multi-column thành stack khi content không còn đủ width.
- Horizontal controls phải wrap/scroll/collapse có chủ đích.
- Full-bleed image cần art direction, không chỉ `object-fit: cover` mặc định.

## Acceptance criteria

- [ ] Có rule extraction trước implementation.
- [ ] Brand/reference boundaries rõ.
- [ ] Components map về design system.
- [ ] Desktop + mobile được kiểm riêng.
- [ ] Không dùng asset/copy không có quyền.
- [ ] Không có patch CSS vô tổ chức chỉ để pixel-match.
