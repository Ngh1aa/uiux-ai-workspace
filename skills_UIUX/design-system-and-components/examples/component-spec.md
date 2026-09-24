# Example — Product Card contract

## Purpose
Tóm tắt sản phẩm trong listing để user nhận diện, so sánh sơ bộ và đi tới detail/save.

## Anatomy
Image → category/eyebrow → product name → essential attributes → optional price/status → actions.

## Variants
- `default`: listing grid.
- `compact`: dense comparison/search suggestion only.

Không có `red`, `homepage`, `special` variants; visual role đến từ tokens/context.

## States
- default/hover/focus;
- unavailable;
- saved;
- image missing;
- loading skeleton.

## Responsive
Mobile giữ tap target/action rõ; attributes có thể giảm xuống essential subset nhưng không ẩn thông tin quyết định mua quan trọng.

## Accessibility
Card title link là primary navigation target. Save là button riêng có accessible name/state. Không bọc cả card bằng nested interactive link.
