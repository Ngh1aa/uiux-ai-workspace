# Chuyển động

Khi nào có chuyển động, nhanh bao nhiêu, theo đường cong nào. Mẫu code ở skill
[`motion-and-microinteractions`](../skills_UIUX/motion-and-microinteractions/SKILL.md).

## 1. Chỉ khi có việc

Mỗi chuyển động phải làm một trong bốn việc, nếu không thì bỏ: **phản hồi** (nút lún, công tắc trượt),
**liên tục** (sheet trượt từ đáy, chi tiết mở từ dòng được chọn), **trạng thái** (tiến độ, dấu tích khi lưu),
**chú ý** (badge mới nảy một lần). App không có chuyển động trang trí; landing được một khoảnh khắc trình diễn.

## 2. Thời lượng và đường cong

| Token | Thời lượng | Dùng cho |
|---|---|---|
| `duration.fast` | 120 ms | Hover, nhấn, công tắc, tooltip |
| `duration.base` | 200 ms | Menu, đổi tab, toast |
| `duration.slow` | 320 ms | Sheet, modal, chuyển màn |

Không thao tác nào chờ quá ~400 ms; đóng nhanh hơn mở (70–80%). `easing.enter` cho vật xuất hiện,
`easing.exit` cho vật rời đi, `easing.standard` cho vật di chuyển; `linear` chỉ cho thanh tiến độ.
Hiệu ứng nảy chỉ cho phản hồi vui (thả tim), không cho modal hay sheet.
Chỉ animate `transform` và `opacity`; mở rộng chiều cao bằng `grid-template-rows: 0fr → 1fr`.

## 3. Giảm chuyển động

Khi hệ điều hành bật giảm chuyển động: thay trượt và phóng bằng mờ dần hoặc đổi ngay, tắt chuyển động tự chạy,
giữ phản hồi trạng thái. Chuyển động tự chạy quá 5 giây phải có nút dừng (WCAG 2.2.2).

Tự kiểm: quay màn ở 0,25×; bật giảm chuyển động và đi lại luồng chính; bấm liên tục 5 lần xem có chồng hay khoá.

Nguồn chính: Material 3 *Motion*, Apple HIG *Motion*, MDN `prefers-reduced-motion`.
