# Chuyển động

Trang này trả lời: **khi nào nên có chuyển động, nhanh bao nhiêu, theo đường cong nào?** Phần làm cụ thể
(mẫu code, vi tương tác) nằm trong skill
[`motion-and-microinteractions`](../skills_UIUX/motion-and-microinteractions/SKILL.md).

## 1. Chuyển động phải có việc để làm

Mỗi chuyển động trả lời được một trong bốn câu, nếu không thì bỏ:

| Việc | Ví dụ |
|---|---|
| **Phản hồi:** "đã nhận thao tác" | Nút lún khi bấm, công tắc trượt, ô nhập rung nhẹ khi sai |
| **Liên tục:** "cái mới đến từ đâu" | Sheet trượt từ đáy, chi tiết mở rộng từ dòng được chọn |
| **Trạng thái:** "đang làm, xong rồi" | Thanh tiến độ, skeleton, dấu tích hiện ra khi lưu |
| **Chú ý:** "nhìn chỗ này" | Badge mới nảy một lần, con số đếm lên khi vào màn |

Chuyển động trang trí (nền trôi, icon lắc liên tục, mọi thứ trượt vào khi cuộn) làm chậm người dùng và
tốn pin. Landing được phép có một khoảnh khắc trình diễn, app thì không.

## 2. Thời lượng

| Token | Thời lượng | Dùng cho |
|---|---|---|
| `duration.instant` | 0 ms | Đổi trạng thái không cần chuyển tiếp; chế độ giảm chuyển động |
| `duration.fast` | 120 ms | Hover, nhấn, công tắc, tooltip |
| `duration.base` | 200 ms | Mở menu, đổi tab, hiện toast |
| `duration.slow` | 320 ms | Sheet, modal, chuyển màn, mở rộng vùng lớn |

Quy tắc: vật càng to, đi càng xa thì càng lâu; nhưng không thao tác nào của người dùng phải chờ quá
khoảng 400 ms. Đóng nhanh hơn mở (khoảng 70–80% thời lượng mở), vì người dùng đã quyết định rời đi.

## 3. Đường cong

| Token | Khi nào |
|---|---|
| `easing.standard` | Vật đi từ chỗ này sang chỗ khác trong màn |
| `easing.enter` | Vật xuất hiện: vào nhanh, chậm dần khi tới chỗ |
| `easing.exit` | Vật biến mất: bắt đầu chậm, rời nhanh |

Không dùng `linear` cho vật chuyển động (trông máy móc); `linear` chỉ hợp cho thanh tiến độ và vòng quay.
Hiệu ứng nảy (spring, overshoot) dùng tiết kiệm, cho phản hồi vui như thả tim, không cho modal.

## 4. Chỉ animate thứ rẻ

Trình duyệt vẽ mượt `transform` và `opacity`. Animate `width`, `height`, `top`, `margin`, `box-shadow` buộc
tính lại bố cục mỗi khung hình và giật trên điện thoại yếu. Mở rộng chiều cao thì dùng `grid-template-rows:
0fr → 1fr` hoặc `transform: scaleY` cho phần nền.

## 5. Giảm chuyển động

Một số người bị chóng mặt, buồn nôn với chuyển động lớn (rối loạn tiền đình). Khi hệ điều hành bật
"giảm chuyển động":

- Thay trượt và phóng to bằng mờ dần (`opacity`) hoặc đổi ngay.
- Tắt chuyển động tự chạy, parallax, video nền tự phát.
- Giữ phản hồi trạng thái (dấu tích, đổi màu) vì nó mang thông tin.

`components.css` đã có khối `@media (prefers-reduced-motion: reduce)`; CSS của dự án phải theo cùng cách.
Chuyển động tự chạy quá 5 giây phải có nút dừng (WCAG 2.2, tiêu chí 2.2.2).

## 6. Tự kiểm tra

- Quay màn hình ở tốc độ 0,25×: chuyển động có kể đúng câu chuyện "từ đâu tới, đi đâu" không?
- Bật giảm chuyển động trong hệ điều hành và đi lại luồng chính.
- Bấm liên tục 5 lần: animation có xếp hàng, chồng chéo, hay khoá thao tác không?

## Nguồn

- Material Design 3, *Motion: easing and duration*.
- Apple Human Interface Guidelines, *Motion*.
- W3C, *WCAG 2.2*, tiêu chí 2.2.2 và 2.3.3; MDN, *prefers-reduced-motion*.
- Val Head, *Designing Interface Animation* (2016).
