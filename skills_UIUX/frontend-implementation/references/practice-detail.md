# Thực hành chuyên sâu

Chỉ mở khi cần chi tiết trong mục dưới đây; WORKFLOWS.md vẫn là nguồn định tuyến duy nhất.

# Frontend Implementation

## Goal

Biến spec thành website **đúng behavior và maintainable**, không chỉ pixel gần giống screenshot.

## Before coding

1. Đọc project conventions/stack hiện tại.
2. Inventory routes/components/tokens/assets đã có.
3. Xác định primary user task + page state cần implement.
4. Chọn reuse/refactor/new component có rationale.
5. Xác định constraints: responsive, a11y, content, SEO, performance.

Nếu chưa có system đủ rõ, quay lại `design-system-and-components` thay vì hardcode page.

## Implementation loop

1. Build semantic structure/content hierarchy.
2. Compose layout bằng existing patterns/tokens.
3. Implement P0 components và real content.
4. Add interaction + state feedback.
5. Add responsive behavior theo content/interaction pressure, không theo device model cụ thể.
6. Verify keyboard/focus/semantic behavior.
7. Optimize image/font/script only sau khi đo/identify impact.
8. Run project build/type/lint/test commands có sẵn.
9. Inspect representative viewports và primary flow.
10. Document known limitation, không tự tuyên bố perfect.

## Coding rules

- Reuse before create; refactor before duplicate.
- Semantic HTML before generic divs.
- Keep content/data separate khỏi visual one-offs khi project architecture cho phép.
- Không hardcode magic values lặp lại; promote stable decisions thành token.
- Tránh JS cho behavior CSS/native HTML giải quyết tốt.
- Event/animation không được block primary task.
- Không thêm dependency chỉ để tránh viết vài dòng platform API đơn giản.
- Preserve existing working behavior khi task chỉ yêu cầu visual change. Giữ **hành vi**, không phải giữ
  code giao diện: khi được yêu cầu redesign, sửa và xoá CSS, markup, renderer cũ tại nguồn theo
  [`brownfield-redesign`](../../brownfield-redesign/SKILL.md), có test hành vi bảo vệ.

## Progressive resources

- [Implementation patterns](../references/implementation-patterns.md)
- [Frontend release gate](../checklists/frontend-gate.md)
- [Page composition example](../examples/page-composition.md)

## Output

- Working code changes.
- Relevant tests/verification evidence.
- Changed component/route list nếu task lớn.
- Known issues/assumptions.

## Acceptance criteria

- Primary task works với real states.
- Existing conventions/reuse respected.
- No obvious duplicate components/styles.
- Representative responsive layouts inspected.
- Critical interactions keyboard-usable.
- Build/type/lint/test phù hợp project pass hoặc failure được báo chính xác.
- No fabricated test/Lighthouse evidence.

## Anti-patterns

- Rebuild toàn codebase khi không cần.
- Ngược lại: thêm một file CSS "final layer" với `!important`, hoặc JS vá DOM sau render, thay vì sửa
  file đang sở hữu giao diện.
- Một component 1000 dòng chứa toàn page behavior/style/data.
- Copy screenshot bằng absolute positioning cố định.
- Patch hàng chục media query thay vì sửa layout model.
- Hide problematic mobile content chỉ để hết overflow.
