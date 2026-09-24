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
