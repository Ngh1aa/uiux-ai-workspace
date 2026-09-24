---
name: frontend-architecture-and-refactoring
description: |
  Thiết kế cấu trúc frontend, module boundaries, component reuse, state/data ownership,
  dependency policy và safe refactoring. Dùng trước implementation lớn, khi source đang rối,
  hoặc khi agent cần tổ chức lại code mà không phá behavior/UI hiện có.
---

# Frontend Architecture & Refactoring

## Architecture goals

Code phải dễ tìm, dễ thay, dễ test và khó tạo duplicate behavior.

## Before changing code

1. Inspect repository structure và conventions.
2. Tìm component/util/style tương tự.
3. Xác định entry points và dependency direction.
4. Ghi behavior phải preserve.
5. Chỉ sau đó mới refactor.

## Boundary rules

- Page/template compose features; không chứa toàn bộ low-level UI logic.
- Shared primitive không import page-specific code.
- Feature-specific component chỉ promote lên shared khi có reuse thật.
- Data fetching/state ownership đặt gần nơi cần nhưng tránh duplicate sources of truth.
- Server/client boundary theo framework phải explicit.

## File organization

Ưu tiên predictable naming và colocate file liên quan. Không tạo hàng loạt `utils2`, `helpers-new`, `final-component`.

## Dependency policy

Trước khi thêm package:

- Native/framework capability có đủ không?
- Existing dependency có giải quyết được không?
- Bundle/security/maintenance cost là gì?
- Package còn maintained và compatible version hiện tại không?

## Safe refactor loop

`baseline → small change → test/build → visual/behavior check → commit logically`

Không vừa đổi architecture, visual design, content và data model trong một refactor nếu không bắt buộc.

## CSS/style architecture

- Token first.
- Component styles scoped/predictable.
- Avoid specificity war và global overrides.
- Không patch bằng `!important` hàng loạt.
- Reuse variants/composition trước duplicate classes.

## Acceptance criteria

- [ ] Không duplicate component rõ ràng.
- [ ] Dependency direction hợp lý.
- [ ] New package có rationale.
- [ ] Refactor preserve behavior đã ghi.
- [ ] Build/test pass sau từng change set lớn.
- [ ] Naming/file structure predictable.
