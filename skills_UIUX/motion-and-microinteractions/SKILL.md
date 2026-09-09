---
name: motion-and-microinteractions
description: |
  Thiết kế và implement motion có mục đích cho hover, feedback, disclosure, navigation,
  loading và scroll reveal. Dùng khi website cần animation/microinteraction nhưng phải giữ
  performance, accessibility, reduced-motion và consistency trong toàn design system.
---

# Motion & Microinteractions

## Motion jobs

Animation chỉ nên phục vụ ít nhất một job:

- **Feedback**: action đã nhận.
- **Continuity**: element đến/từ đâu.
- **Hierarchy**: cái gì cần chú ý trước.
- **State change**: open/close, selected, success/error.
- **Delight**: chỉ sau khi usability/performance đã ổn.

Nếu không giải thích được job, bỏ animation.

## Motion system

Định nghĩa token cho duration/easing/distance thay vì mỗi component tự chọn.

- Micro state: nhanh.
- Disclosure/modal: vừa đủ để hiểu transition.
- Page/hero storytelling: dài hơn nhưng không block task.

Không dùng `transition: all` nếu có thể chỉ rõ property.

## Rules

- Ưu tiên transform/opacity cho animation thường xuyên.
- Không animate layout property nặng liên tục nếu không cần.
- Scroll animation chỉ chạy một lần mặc định.
- Không stagger danh sách dài gây chờ đợi.
- Hover không được là cách duy nhất để khám phá information.
- Button press cần immediate feedback.
- Loading dài cần skeleton/progress phù hợp, không spinner vô hạn mơ hồ.

## Reduced motion

`prefers-reduced-motion` là contract bắt buộc. Khi reduce:

- Loại parallax, large translation, auto-scroll, decorative loops.
- Giữ feedback state bằng instant/subtle opacity nếu cần.
- Không làm mất content/functionality.

## Motion spec

Với interaction đáng kể, ghi:

| Trigger | From | To | Duration token | Easing | Reduced-motion |
|---|---|---|---|---|---|

## Page transitions

Không thêm chỉ vì SPA hỗ trợ. Transition không được trì hoãn navigation, reset focus sai hoặc che loading thật.

## Performance gate

- Test trên mobile/CPU chậm hơn desktop dev machine.
- Không gây visible CLS.
- Không tạo long tasks từ scroll listener.
- Dừng animation ngoài viewport nếu loop/media nặng.

## Acceptance criteria

- [ ] Mỗi animation có purpose.
- [ ] Dùng motion tokens.
- [ ] Reduced motion hoạt động.
- [ ] Không block primary task.
- [ ] Không có jank/scroll-linked handler nặng rõ ràng.
- [ ] Focus/keyboard không bị phá bởi transition.
