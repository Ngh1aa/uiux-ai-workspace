---
name: accessibility
description: |
  Thiết kế, implement và review accessibility cho website theo WCAG 2.2 AA. Dùng khi xây
  semantic structure, keyboard/focus behavior, forms, dialogs, media, contrast hoặc khi audit
  UI để bảo đảm primary journeys dùng được bằng keyboard, screen reader và zoom/reflow.
---

# Accessibility

## Goal

Build accessibility **into** component/flow, không bolt-on ở cuối. Ưu tiên native HTML semantics; ARIA chỉ bổ sung khi native element/pattern không đủ.

## Use with

- `interaction-patterns-and-form-ux` cho form/search/filter/dialog.
- `responsive-and-device-strategy` cho zoom/reflow/touch.
- `design-system-and-components` để accessibility contract nằm trong component spec.
- `testing-strategy` cho regression evidence.

## Workflow

1. **Identify critical journeys** và interaction có rủi ro cao.
2. **Semantic pass**: landmarks, headings, controls, labels, relationships.
3. **Keyboard pass**: tab order, activation keys, escape/arrow behavior khi pattern yêu cầu.
4. **Focus pass**: visible focus, focus move/return, no trap ngoài intentional modal trap.
5. **Name/state pass**: accessible names, descriptions, errors, expanded/selected/busy/live state.
6. **Visual pass**: contrast, color independence, zoom/reflow, text spacing, focus visibility.
7. **Media pass**: alt strategy, captions/transcripts khi cần, decorative assets hidden correctly.
8. **Motion pass**: reduced-motion behavior và không tạo motion gây cản trở task.
9. **Manual verification** trước khi tuyên bố pass; automated tools chỉ là một signal.

## Decision rules

- `<button>` tốt hơn `div role="button"`.
- Label visible tốt hơn placeholder-only.
- Không dùng màu là tín hiệu duy nhất.
- Error phải nói **field nào + vấn đề gì + cách sửa**.
- Modal mở phải có accessible name, focus vào context hợp lý, Escape khi pattern cho phép và return focus khi đóng.
- Custom widget chỉ dùng khi native control thật sự không đáp ứng UX.
- Không thêm ARIA dư để “trông accessible”. Bad ARIA có thể làm trải nghiệm tệ hơn.

## Progressive resources

Chỉ đọc file cần thiết:

- [Implementation reference](references/implementation-reference.md): semantics, keyboard, focus, form, media, ARIA patterns.
- [Manual QA checklist](checklists/a11y-gate.md): release gate.
- [Accessible form example](examples/accessible-form.md): concrete pattern.

## Output

Tùy task, output một hoặc nhiều:
- accessibility contract trong component spec;
- audit findings theo severity + affected journey + fix;
- manual keyboard/screen-reader/zoom evidence;
- known limitations.

## Acceptance criteria

- Critical journeys usable bằng keyboard.
- Focus visible và logical.
- Form controls có programmatic name/label; errors announced/useful.
- Heading/landmark structure có nghĩa.
- Contrast/non-color indicators phù hợp target WCAG.
- Zoom/reflow không làm mất task/content quan trọng.
- Reduced motion được tôn trọng khi motion không thiết yếu.
- Automated critical/serious issues được triage; manual checks hoàn tất theo scope.

## Never claim

Không nói “WCAG compliant/100% accessible” chỉ dựa vào Lighthouse/axe. Nêu rõ **đã kiểm gì**, **chưa kiểm gì** và evidence.
