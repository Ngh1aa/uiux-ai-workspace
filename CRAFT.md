# Chuẩn tay nghề

Một trang, đọc ở mọi việc từ cỡ S trở lên, sau `TASTE.md` và trước khi dựng. Bốn phần: lên kế hoạch
thị giác, danh sách cấm, số liệu cốt lõi, ảnh và icon. Chi tiết đầy đủ ở
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
Một điểm táo bạo:      <chỗ duy nhất dồn sự chú ý: một con số lớn, một hoạ tiết, một chuyển động>
Ba điểm khác starter:  1. <...> 2. <...> 3. <...>
Đã đối chiếu mục 2:    <liệt kê mặc định nào gần chạm và đã đổi thế nào>
```

Một điểm táo bạo là đủ. Cả trang cùng gào thì không chỗ nào nổi.

## 2. Danh sách cấm: các mặc định làm thiết kế trông như AI làm

Mỗi dòng là tín hiệu cần xem xét, không phải điều cấm tuyệt đối. Giữ khi có lý do từ brief,
design system hiện có, tác vụ, nền tảng hoặc khả năng tiếp cận; ghi ngắn bối cảnh, đánh đổi và
cách kiểm chứng trên màn render. Không đổi font, màu hay cấu trúc chỉ để né checklist.

**Chữ**
- Inter, Roboto, Arial, Open Sans, Lato hay font hệ thống làm font duy nhất của trang.
- Một font, một độ đậm cho mọi thứ; phân cấp chỉ bằng cỡ chữ.
- Nhãn nhỏ IN HOA giãn chữ (eyebrow) phía trên mọi tiêu đề.
- Font không có bộ chữ tiếng Việt cho nội dung tiếng Việt (DM Sans, Outfit, Instrument Sans...), hoặc
  thiếu ký tự ₫ mà vẫn dùng cho giá tiền.

**Màu**
- Gradient tím–xanh trên nền trắng; gradient làm nền mặc định cho hero.
- Nền kem với điểm nhấn đất nung; nền gần đen với xanh chuối axit. Hai bảng màu "có gu" mặc định.
- Màu thương hiệu rải đều khắp nơi thay vì để dành cho 5–10% diện tích.
- Chấm trạng thái xanh/đỏ không gắn với trạng thái thật.

**Bố cục**
- Hero căn giữa: tiêu đề, một dòng mô tả, hai nút, ảnh minh hoạ trừu tượng.
- Ba card tính năng giống hệt nhau, mỗi card một icon trong vòng tròn.
- Section nào cũng "tiêu đề + 3 card"; mọi khối đều là card bo tròn; card lồng card.
- Mọi thứ căn giữa; mọi section cùng chiều cao và khoảng cách.
- Thanh màu bên trái mỗi khối, mỗi khối một màu.

**Chi tiết**
- Emoji làm icon, bullet hay nút.
- Nối cụm từ bằng " · "; mũi tên "→" sau mọi liên kết.
- Glassmorphism, glow, bóng đổ dày dùng làm trang trí khắp nơi.
- Số liệu, lời chứng thực, logo khách hàng bịa trông như thật mà không ghi "minh hoạ".
- "Lorem ipsum", "John Doe", "Acme Inc".

`static-check.cjs` bắt được một phần danh sách này (font mặc định, gradient tím, eyebrow, emoji,
" · "). Phần còn lại phải nhìn ảnh.

## 3. Số liệu cốt lõi

| Hạng mục | Chuẩn |
|---|---|
| Khoảng cách | Bội số của 4, nhịp 8. Trong nhóm nhỏ hơn giữa nhóm ít nhất 1,5 lần. Tối đa 4–5 giá trị khoảng cách mỗi màn |
| Lề màn | Điện thoại 16–20, tablet 24, desktop 32–40; nội dung tối đa 1200–1280, chữ dài 640–720 |
| Thang chữ | App 1,125–1,2, thân 15–17. Marketing 1,25–1,333, thân 17–20. Tiêu đề lớn tracking âm 1–2,5% |
| Line-height | Thân 1,5–1,6 (tiếng Việt ≥ 1,5), tiêu đề 1,2–1,3, display ~1,1 |
| Font | Tối đa 2 họ, 2–3 độ đậm. Số trong bảng và giá: `tabular-nums` |
| Màu | 70–80% trung tính, 15–25% cấu trúc, 5–10% thương hiệu. Một nút chính tô đầy mỗi vùng |
| Tương phản | Chữ 4,5:1, chữ lớn 3:1, viền điều khiển và focus 3:1, cả sáng và tối |
| Vùng chạm | iOS 44 pt, Android 48 dp, web tối thiểu 24 px (chạm: 44), cách nhau ≥ 8 |
| Breakpoint web | 600, 840, 1200, 1600; soát ở 390, 768, 1280, 1440 |
| Bo góc | Một bán kính cho mỗi loại bề mặt; bo trong = bo ngoài − padding |
| Chuyển động | 100–150 ms hover và bật tắt, 200–250 ms mở rộng, 300–400 ms sheet và modal; tôn trọng giảm chuyển động |
| Trạng thái | Mặc định, hover/nhấn, focus, tắt, đang tải, rỗng, lỗi, nội dung dài, chữ phóng 200% |

Các con số về tỷ lệ màu, số bước spacing, thang chữ và breakpoint là điểm xuất phát cho màn
chưa có hệ thống riêng. Dashboard mật độ cao, nội dung dài và control nền tảng có thể cần nhịp
khác. Giữ ngưỡng tương phản, vùng chạm và khả năng phóng chữ; không thu nhỏ chữ hay giấu dữ liệu
quan trọng để đạt tỷ lệ thẩm mỹ. Với font, kiểm tra đúng file font được dùng, dấu tiếng Việt và ₫
trên render; tên họ font không đủ để kết luận có hoặc thiếu glyph.

## 4. Ảnh và icon

**Ảnh, theo thứ tự ưu tiên**
1. Ảnh khách cung cấp. Hỏi trong brand brief (mục 8).
2. Ảnh stock có giấy phép dùng thương mại (Unsplash, Pexels). Ghi nguồn và tên tác giả trong ghi
   chú giao; không dùng ảnh có người nhận diện được trong ngữ cảnh nhạy cảm.
3. Khung giữ chỗ có ghi chú: khối màu bề mặt, đúng tỉ lệ ảnh thật, chú thích "Ảnh: <mô tả cần
   chụp>". Tốt hơn ảnh stock lạc tông.

Không dùng: ảnh AI tạo người thật hoặc sản phẩm thật trông như ảnh chụp, ảnh lấy từ web khác không
rõ giấy phép, ảnh chèn chữ không đọc được. Ảnh có chữ đè lên phải qua kiểm tra tương phản ở vùng chữ.
Ảnh luôn có `alt` mô tả nội dung (ảnh trang trí: `alt=""`), có `width`/`height` để không nhảy bố cục.

**Icon**
1. Bộ icon của design system khi đủ: `design-system/components/icons.svg` (32 icon) và
   `design-system/starter/icons-app.svg` (11 icon).
2. Thiếu thì lấy từ **Lucide** (ISC) hoặc **Phosphor** (MIT), một bộ cho cả dự án, cùng độ dày nét
   với bộ sẵn có (1,75 px ở 24 px, đầu nét tròn). Chép SVG vào dự án, ghi tên bộ và giấy phép trong ghi chú giao.
   Không chép cả bộ vào repo này.
3. App native: SF Symbols (iOS), Material Symbols (Android).

Cỡ: 16 trong dòng chữ, 20 mặc định, 24 điều hướng. Icon đi kèm nhãn trong điều hướng; nút chỉ có
icon phải có `aria-label`. Không trộn hai bộ icon, không dùng emoji thay icon.
