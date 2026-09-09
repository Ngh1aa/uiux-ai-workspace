---
name: interaction-patterns-and-form-ux
description: |
  Thiết kế interaction patterns cho navigation, forms, search, filters, tabs, accordions,
  dialogs, drawers, onboarding và feedback states. Dùng khi website có task tương tác,
  form lead, catalogue, search/filter hoặc flow nhiều bước cần UX rõ và accessible.
---

# Interaction Patterns & Form UX

## Core rule

Mỗi interaction phải trả lời: **user thấy gì → làm gì → hệ thống phản hồi gì → lỗi thì phục hồi thế nào**.

## Pattern selection

Không chọn component theo trend. Chọn dựa trên task:

- Tabs: chuyển giữa peer views, không dùng để giấu content dài tùy tiện.
- Accordion: progressive disclosure cho sections độc lập.
- Modal: task ngắn, blocking hoặc confirmation; không dùng như page thay thế.
- Drawer: contextual secondary task; đảm bảo focus management.
- Dropdown: compact choices; tránh menu sâu nhiều tầng trên mobile.

## Forms

### Field rules

- Label luôn tồn tại; placeholder không thay label.
- Hỏi ít nhất có thể để đạt task.
- Group field theo mental model.
- Dùng input type/autocomplete phù hợp.
- Required/optional phải rõ.
- Validation gần field và nói cách sửa.
- Không xóa dữ liệu user sau lỗi submit.

### Multi-step form

Chỉ chia bước khi giảm cognitive load thật. Hiển thị progress có ý nghĩa, cho back mà không mất data và nói rõ bước cuối tạo ra điều gì.

## Search

- Search box label/placeholder thể hiện scope.
- Support typo/empty query theo khả năng hệ thống.
- Results phải giải thích query/filter đang áp dụng.
- Không có kết quả: đưa recovery action, không chỉ thông báo.

## Filters

- Filter state phải visible.
- Cho clear all + clear từng filter.
- Mobile dùng drawer/sheet nếu controls nhiều.
- Hiển thị result count khi hữu ích.
- URL/state persistence nếu user cần share/back/forward.

## Navigation

- Active state rõ.
- Labels theo ngôn ngữ user, không theo org chart nội bộ.
- Primary navigation không biến thành collection CTA hỗn loạn.
- Mobile menu phải keyboard/focus/scroll-lock đúng.

## Feedback contract

Mọi action async cần:

`idle → pending → success | error → recovery`

Không để user click lặp vì thiếu pending state.

## Destructive actions

- Confirmation chỉ khi hậu quả đáng kể.
- Button label nói đúng action: “Xóa dự án”, không “OK”.
- Nếu có thể undo, ưu tiên undo hơn modal cảnh báo liên tục.

## Output

Với flow phức tạp, tạo `docs/interaction-spec.md` gồm pattern, state diagram, keyboard behavior, validation và recovery.

## Acceptance criteria

- [ ] Primary interactions có state model.
- [ ] Form labels/errors/recovery rõ.
- [ ] Search/filter có empty/no-result behavior.
- [ ] Keyboard + focus behavior xác định.
- [ ] Mobile interaction không chỉ là desktop thu nhỏ.
- [ ] Destructive action có guardrail phù hợp.
