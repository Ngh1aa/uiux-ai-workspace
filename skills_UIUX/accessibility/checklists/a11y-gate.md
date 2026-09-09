# Accessibility Release Gate

## Structure
- [ ] `html` language đúng.
- [ ] Landmarks và heading hierarchy có nghĩa.
- [ ] Interactive semantics native khi có thể.

## Keyboard/focus
- [ ] Tab order logical.
- [ ] Mọi critical control keyboard-operable.
- [ ] Focus visible.
- [ ] Menu/dialog/popover có open/close/focus behavior đúng.
- [ ] Không keyboard trap ngoài intentional modal containment.

## Forms/status
- [ ] Labels programmatically associated.
- [ ] Errors cụ thể và được expose.
- [ ] User data không mất vô lý khi error.
- [ ] Async success/error/loading có feedback đủ.

## Visual/media
- [ ] Contrast checked trên representative states.
- [ ] Không truyền meaning bằng màu בלבד.
- [ ] Alt/decorative handling đúng.
- [ ] Captions/transcript khi media cần.
- [ ] Reduced motion respected.

## Manual evidence
- [ ] Keyboard pass critical journeys.
- [ ] Representative screen-reader smoke test khi scope yêu cầu.
- [ ] Zoom/reflow test.
- [ ] Automated audit triaged; không chỉ chụp score.
