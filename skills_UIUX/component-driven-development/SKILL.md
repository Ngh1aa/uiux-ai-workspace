---
name: component-driven-development
description: |
  Xây UI theo Component-Driven Development: component isolation, state stories/examples,
  composition từ primitive đến page và visual/accessibility tests. Dùng với design system,
  Storybook hoặc bất kỳ project nào có nhiều reusable component và UI states.
---

# Component-Driven Development

## Principle

Build complexity **bottom-up** nhưng validate experience **top-down**.

`tokens → primitives → components → patterns → sections → pages`

Không biến mọi wrapper thành component; component phải có reuse, state, behavior hoặc semantic value rõ.

## Component contract

Mỗi component reusable xác định:

- Purpose.
- Props/API.
- Slots/composition.
- Variants.
- States.
- Responsive behavior.
- Accessibility behavior.
- Content constraints.

## State matrix

Tạo ít nhất các state có liên quan:

`default / hover / focus / active / disabled / loading / error / empty / selected`

Không chỉ demo happy path với content đẹp hoàn hảo.

## Isolation workflow

1. Build primitive/component với mock data.
2. Render representative variants.
3. Test long/short/missing content.
4. Test keyboard/focus.
5. Test responsive width.
6. Compose thành pattern/section.
7. Assemble page và validate real journey.

Nếu dùng Storybook, stories là executable examples chứ không phải gallery decoration.

## API quality

- Prefer semantic prop (`tone="danger"`) hơn style prop tùy tiện (`red=true`).
- Avoid boolean explosion.
- Avoid component-specific magic spacing prop nếu layout parent nên quản lý gap.
- Controlled/uncontrolled behavior phải có chủ đích.

## Visual regression

Chụp/test các state quan trọng và viewport đại diện. Thay đổi token/component phải xem downstream impact trước merge.

## Acceptance criteria

- [ ] Component inventory map về design system.
- [ ] Reusable components có state coverage.
- [ ] Long/empty/error content được test.
- [ ] Keyboard/focus được test.
- [ ] API không phản ánh raw CSS tùy tiện.
- [ ] Page cuối vẫn được review theo user journey.
