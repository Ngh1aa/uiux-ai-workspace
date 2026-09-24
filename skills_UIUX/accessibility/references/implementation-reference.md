# Accessibility Implementation Reference

Đọc file này khi task cần implementation chi tiết.

## Semantic structure

- Một `main` chính; landmark có label khi có nhiều landmark cùng loại.
- Heading phản ánh document hierarchy, không chọn heading chỉ vì size.
- Interactive action dùng `button`; navigation dùng `a` có `href`.
- Group controls liên quan bằng `fieldset`/`legend` khi semantics phù hợp.

## Keyboard & focus

Global expectations:
- `Tab`/`Shift+Tab`: di chuyển focus giữa interactive controls.
- `Enter`: activate link/button theo native behavior.
- `Space`: button/checkbox theo native behavior.
- `Escape`: đóng temporary layer khi interaction pattern quy định.

Focus rules:
- Luôn có visible `:focus-visible`.
- Không `outline: none` nếu không có equivalent focus indicator.
- Opening modal/menu không được làm mất focus context.
- Closing temporary UI trả focus về trigger nếu trigger còn tồn tại.
- Không dùng positive `tabindex` để vá DOM order.

## Forms

Mỗi field cần:
- visible label;
- help text khi format/constraint không obvious;
- `autocomplete` phù hợp với common personal fields;
- inline error cụ thể;
- `aria-describedby` khi cần nối help/error;
- `aria-invalid="true"` khi invalid.

Khi submit có nhiều lỗi:
- focus hoặc đưa user tới error summary nếu form dài;
- summary link tới field;
- dữ liệu hợp lệ đã nhập không bị reset.

## Status & async UI

- Loading kéo dài: expose busy/status semantics phù hợp.
- Success/error sau async action cần feedback visual và khi cần screen-reader announcement.
- Không spam `aria-live`; chỉ announce thông tin user cần để tiếp tục task.

## Images & media

- Informative image: alt mô tả purpose/content cần thiết trong context.
- Decorative image: `alt=""`.
- Complex chart: cung cấp text equivalent/table/description đủ để hiểu insight chính.
- Video có speech quan trọng: captions; cân nhắc transcript/audio description theo content.

## Dialog pattern

Ưu tiên native `<dialog>` khi phù hợp và implementation/browser target cho phép. Với custom dialog:
- accessible name;
- modal semantics đúng;
- focus initial có chủ ý;
- focus contained trong modal khi modal thực sự blocking;
- restore focus khi đóng;
- background không interactive.

## Contrast & visual access

Target project hiện dùng WCAG 2.2 AA. Khi cần threshold cụ thể, verify current official W3C criterion thay vì dựa vào memory. Đặc biệt review:
- normal/large text;
- component boundaries/meaningful graphics;
- focus indicator;
- disabled state không cần truyền information chỉ bằng low contrast.

## Zoom/reflow

Test content và critical task ở zoom lớn / narrow reflow. Không dùng horizontal scroll cho text content trừ content bản chất cần 2D (ví dụ bảng lớn/canvas) và có strategy usable.
