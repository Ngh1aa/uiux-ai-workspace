# Component Contracts

Mỗi reusable component nên document tối thiểu:

```markdown
## Component: Button
Purpose:
Anatomy:
Variants:
Sizes:
States:
Content rules:
Responsive behavior:
Keyboard/accessibility:
Composition rules:
Do / Don't:
```

## Variant test

Tạo variant mới chỉ khi ít nhất một điều đúng:
- semantic role khác;
- hierarchy/action priority khác;
- behavior/state contract khác;
- reusable use-case lặp lại ở nhiều context.

Không tạo variant vì:
- một screenshot có border khác 1px;
- một page muốn margin riêng;
- muốn tránh sửa layout parent.

## Composition

Components không nên sở hữu outer page margins tùy tiện. Parent pattern/section/grid quản layout spacing; component quản internal layout.

## State coverage

Không phải component nào cũng cần mọi state. Nhưng mọi state có thể xảy ra phải được thiết kế rõ; đặc biệt focus, disabled, loading, error, selected/expanded.
