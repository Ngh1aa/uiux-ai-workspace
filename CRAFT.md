# Chuẩn tay nghề

Đọc ở mọi việc từ cỡ S trở lên, sau `TASTE.md` và trước khi dựng. Chi tiết đầy đủ ở
[craft standards](skills_UIUX/ui-craft-and-visual-qa/references/craft-standards.md).

## 1. Lên kế hoạch thị giác trước khi viết code

Viết ra khối dưới đây trong câu trả lời (hoặc ghi chú giao), rồi đối chiếu từng dòng với mục 2.
Dòng nào trùng một mặc định bị cấm mà brief không yêu cầu thì sửa kế hoạch **trước** khi dựng.

```text
Ngành và vật gốc:      <ngành>; vật gốc <...> (SIGNATURE.md bước 1)
Một câu cảm giác:      <ví dụ: "ấm, chậm, thủ công, như tờ phiếu hẹn viết tay">
Chữ:                   tiêu đề <font, cỡ, độ đậm>; thân <font, cỡ, line-height>; có tiếng Việt: có
Màu theo vai trò:      nền <hex>, bề mặt <hex>, chữ <hex>, thương hiệu <hex>, nhấn <hex>, (tuỳ) <hex>
Hình khối:             bo góc <px>; viền hay bóng; độ dày nét
Bố cục màn chính:      <phác ASCII 5–10 dòng: khối nào ở đâu, thứ tự đọc>
Lưới và mật độ:        <số cột ở 390/1280; mật độ thoáng|vừa|gọn; khối nào lấp phần còn lại của khung>
Card nổi bật:          <3 tầng: nhãn; thông tin chính; ngữ cảnh (so sánh, tiến độ, hạn)>
Một điểm táo bạo:      <chỗ duy nhất dồn sự chú ý: một con số lớn, một hoạ tiết, một chuyển động>
Ba điểm khác starter:  1. <...> 2. <...> 3. <...>
Đã đối chiếu mục 2:    <liệt kê mặc định nào gần chạm và đã đổi thế nào>
```

Một điểm táo bạo là đủ. Cả trang cùng gào thì không chỗ nào nổi.

## 2. Danh sách cấm: các mặc định làm thiết kế trông như AI làm

Mỗi dòng là mặc định cần tránh. Chỉ giữ khi brief, design system của khách hoặc nền tảng yêu cầu rõ;
ghi lý do trong phần bàn giao. Các dòng cấm của `TASTE.md` (vạch trái, " · ", dòng giải thích phụ, hoạ tiết
đè chữ, gradient, glow, ô icon nhiều màu, overline, emoji) không có ngoại lệ ngoài brief.

**Chữ**
- Inter, Roboto, Arial, Open Sans, Lato hay font hệ thống làm font duy nhất của trang.
- Một font, một độ đậm cho mọi thứ; phân cấp chỉ bằng cỡ chữ.
- Font không có bộ chữ tiếng Việt cho nội dung tiếng Việt (DM Sans, Outfit, Instrument Sans...), hoặc
  thiếu ký tự ₫ mà vẫn dùng cho giá tiền.

**Màu**
- Nền kem với điểm nhấn đất nung; nền gần đen với xanh chuối axit. Hai bảng màu "có gu" mặc định.
- Màu thương hiệu rải đều khắp nơi thay vì để dành cho 5–10% diện tích.
- Chấm trạng thái xanh/đỏ không gắn với trạng thái thật.

**Bố cục**
- Hero căn giữa: tiêu đề, một dòng mô tả, hai nút, ảnh minh hoạ trừu tượng.
- Ba card tính năng giống hệt nhau, mỗi card một icon trong vòng tròn.
- Section nào cũng "tiêu đề + 3 card"; mọi khối đều là card bo tròn; card lồng card.
- Mọi thứ căn giữa; mọi section cùng chiều cao và khoảng cách.
- Màn desktop chỉ dùng một cột hẹp, nửa phải bỏ trống; mảng trống lớn ở đáy màn hoặc đáy card.
- Card nổi bật chỉ có một con số trên nền màu; card nào cũng chỉ một tiêu đề và một dòng phụ.
- Kéo giãn khoảng cách hoặc chiều cao khung để "lấp" màn thay vì sắp lại bố cục.

**Chi tiết**
- Mũi tên "→" sau mọi liên kết.
- Số liệu, lời chứng thực, logo khách hàng bịa trông như thật mà không ghi chú "minh hoạ" trong phần bàn giao.
- "Lorem ipsum", "John Doe", "Acme Inc".

`static-check.cjs` và `taste-check.cjs` bắt một phần danh sách này; phần còn lại phải nhìn ảnh.

## 3. Số liệu cốt lõi

| Hạng mục | Chuẩn |
|---|---|
| Khoảng cách | Bội số của 4, nhịp 8. Trong nhóm nhỏ hơn giữa nhóm ít nhất 1,5 lần. Tối đa 4–5 giá trị khoảng cách mỗi màn |
| Lề màn | Điện thoại 16–20, tablet 24, desktop 32–40; nội dung tối đa 1200–1280, chữ dài 640–720 |
| Lưới và mật độ | Desktop 12 cột, gutter 24; mật độ theo loại màn trong [layout-and-density](foundations/layout-and-density.md). Khoảng trống dọc liền mạch tối đa ~160 px trong một màn app |
| Thang chữ | App 1,125–1,2, thân 15–17. Marketing 1,25–1,333, thân 17–20. Tiêu đề lớn tracking âm 1–2,5%. Chi tiết tiếng Việt: [typography-vietnamese](foundations/typography-vietnamese.md) |
| Line-height | Thân 1,5–1,6 (tiếng Việt ≥ 1,5), tiêu đề 1,2–1,3, display ~1,1 |
| Font | Tối đa 2 họ, 2–3 độ đậm. Số trong bảng và giá: `tabular-nums` |
| Màu | 70–80% trung tính, 15–25% cấu trúc, 5–10% thương hiệu. Một nút chính tô đầy mỗi vùng. Dựng thang: [color-oklch](foundations/color-oklch.md) |
| Tương phản | Chữ 4,5:1, chữ lớn 3:1, viền điều khiển và focus 3:1, cả sáng và tối |
| Vùng chạm | iOS 44 pt, Android 48 dp, web tối thiểu 24 px (chạm: 44), cách nhau ≥ 8 |
| Breakpoint web | 600, 840, 1200, 1600; soát ở 390, 768, 1280, 1440 |
| Bo góc | Một bán kính cho mỗi loại bề mặt; bo trong = bo ngoài − padding |
| Chuyển động | 100–150 ms hover và bật tắt, 200–250 ms mở rộng, 300–400 ms sheet và modal; tôn trọng giảm chuyển động. Xem [motion](foundations/motion.md) |
| Trạng thái | Mặc định, hover/nhấn, focus, tắt, đang tải, rỗng, lỗi, nội dung dài, chữ phóng 200% |

Các con số về tỷ lệ màu, số bước spacing, thang chữ và breakpoint là điểm xuất phát cho màn
chưa có hệ thống riêng. Dashboard mật độ cao, nội dung dài và control nền tảng có thể cần nhịp
khác. Giữ ngưỡng tương phản, vùng chạm và khả năng phóng chữ; không thu nhỏ chữ hay giấu dữ liệu
quan trọng để đạt tỷ lệ thẩm mỹ. Với font, kiểm tra đúng file font được dùng, dấu tiếng Việt và ₫
trên render; tên họ font không đủ để kết luận có hoặc thiếu glyph.

## 4. Ảnh và icon

Ảnh: của khách trước, rồi stock có giấy phép, rồi khung giữ chỗ có ghi chú; luôn có `alt`, `width`, `height`.
Icon: bộ của design system, thiếu thì một bộ Lucide hoặc Phosphor cùng nét; không trộn bộ, không emoji.
Thứ tự ưu tiên, giấy phép và cỡ: [ảnh và icon](foundations/images-and-icons.md).
