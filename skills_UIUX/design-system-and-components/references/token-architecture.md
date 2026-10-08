# Token Architecture

## Layers

### Primitive
Raw palette/scale values. Ví dụ:
```text
color.blue.600
space.4
radius.2
```
Không dùng primitive trực tiếp khắp app nếu semantic role đã tồn tại.

### Semantic
Mô tả purpose:
```text
color.bg.canvas
color.bg.brand
color.text.primary
color.text.on-brand
color.border.subtle
color.action.primary.bg
color.focus.ring
```

### Component
Chỉ tạo khi component thật sự cần stable local contract:
```text
button.primary.bg
button.primary.bg-hover
input.border-invalid
nav.height
```

## Token checklist

Mỗi token cần trả lời:
- Nó giải quyết semantic decision nào?
- Theme/brand mode có đổi không?
- Có token gần nghĩa đã tồn tại không?
- Component nào consume?

## CSS mapping example

```css
:root {
  --primitive-indigo-600: #4f46e5;
  --color-action-primary-bg: var(--primitive-indigo-600);
  --color-text-primary: #171717;
  --space-section-block: clamp(4rem, 8vw, 8rem);
}
```

Không bắt buộc naming này; điều quan trọng là layer/meaning nhất quán.

## Numeric candidate knowledge — load only for an unresolved scale decision

Existing project tokens và current user constraints đứng trước generic examples. Khi thiếu numeric roles, có thể đọc đúng một nguồn candidate theo concern:

- [Primitive token examples](../../vendor/ui-ux-pro-max/skills/design-system/references/primitive-tokens.md): 4px spacing base và type examples 12–48px; không phải preset bắt buộc.
- [Semantic token examples](../../vendor/ui-ux-pro-max/skills/design-system/references/semantic-tokens.md): phân biệt component, section và page spacing; map về content và page role.
- [Retrieved UX rules](../../vendor/ui-ux-pro-max/engine/data/ux-guidelines.csv): mobile body/readability/reflow và modular scale examples.

Chỉ ADOPT/ADAPT số giải quyết role cụ thể, ghi source và rationale. Không đọc toàn bộ vendor skill để tìm một số. Generic examples không chứng minh industrial-specific scale; free choices còn thiếu phải là professional hypotheses và được kiểm qua actual content/viewport.
