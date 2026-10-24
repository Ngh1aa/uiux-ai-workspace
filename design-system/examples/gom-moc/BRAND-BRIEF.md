# Brand brief: Lò Gốm Mộc (khách hàng giả định)

Ví dụ chạy thử quy trình `START-HERE.md`: brief, kế hoạch thị giác, `brand.css`, landing page và
màn app đặt lớp. Mọi tên, giá, lịch và con số là giả định.

## 1. Khách đưa gì?

Mức **C**: chỉ có logo vẽ tay (chữ "Mộc" trong một vòng tròn không khép kín). Không có guideline,
không có design system. Màu và font dưới đây là `ĐỀ XUẤT`.

## 2. Sản phẩm

- Khách hàng, ngành: xưởng gốm nhỏ ở Bát Tràng, dạy lớp làm gốm cuối tuần 6–8 người.
- Làm gì: landing page đặt lớp + vài màn app đặt lớp trên điện thoại (prototype trình duyệt).
- Người dùng chính: dân văn phòng Hà Nội 25–35 tuổi, muốn một buổi cuối tuần làm tay, chậm lại.
  Việc chính: chọn buổi còn chỗ và giữ chỗ trong dưới 2 phút.
- Ngôn ngữ: tiếng Việt. Dark mode: có, vì app.

## 3. Logo

Chữ "Mộc" viết tay trong vòng tròn hở một góc. Dùng được trên nền sáng và nền men ngọc đậm.

## 4. Màu

| Màu | Hex | Nguồn | Vai trò |
|---|---|---|---|
| Men ngọc đậm | `#2c5a4e` | ĐỀ XUẤT (men celadon Bát Tràng) | Thương hiệu, nút chính, card nổi bật |
| Men ngọc nhạt | `#e3ece8` | ĐỀ XUẤT | Nền nhấn nhẹ, mục đang chọn |
| Xám tro | `#ecebe7` | ĐỀ XUẤT (men tro) | Nền trang |
| Đất nung sẫm | `#9a4a24` | ĐỀ XUẤT | Điểm nhấn hiếm: số chỗ còn ít |
| Mực than | `#1e2421` | ĐỀ XUẤT | Chữ chính |

Tránh có chủ đích: nền kem + điểm nhấn đất nung (mặc định "thủ công" của AI, xem `CRAFT.md`).
Đất nung chỉ dùng cho cảnh báo còn ít chỗ, không làm màu chủ đạo.

## 5. Chữ

- Font chính thức: CHƯA CÓ.
- Đề xuất: tiêu đề **Lora** (có chân, mềm, có tiếng Việt, OFL); thân **Be Vietnam Pro** (có sẵn
  trong design system). Đã gõ thử "Ước mơ Đường phố Hữu Nghị Ỹ Ở 450.000 ₫" ở cỡ 64 và 16: dấu không bị cắt, nhưng
  bản Lora đang có **không có ký tự ₫** (trình duyệt thay bằng font khác, lệch nét). Giá tiền dùng
  Be Vietnam Pro.
- Lora chưa được đóng gói trong repo: bản giao thật phải tự host file woff2 (subset latin +
  vietnamese) cạnh `fonts.css`, kèm `OFL.txt`.

## 6. Giọng điệu

Chậm, ấm, cụ thể. Ba tính từ: mộc, kiên nhẫn, gần gũi. Không dùng chữ IN HOA để hét, không
"trải nghiệm tuyệt vời".

## 7. Tham khảo

Không có (khách chưa gửi). Ghi `UNKNOWN`.

## 8. Dấu ấn riêng

- Vật gốc: **bàn xoay** (vòng tròn đồng tâm) và **vết rạn men**.
- Hình khối: ảnh và card cùng bo 20 px (TASTE: một bán kính); nút bo tròn hẳn như miệng bát.
- Mật độ: thoáng, khoảng cách section lớn.
- Ảnh: khách chưa có ảnh. Dùng khung giữ chỗ có ghi chú; hoạ tiết vòng bàn xoay vẽ bằng SVG.
- Icon: bộ của design system.
- Chuyển động: không cần; giữ tĩnh.
- Số liệu: số chỗ còn lại viết như nhãn dán trên phôi gốm trước khi vào lò.

## 9. Chốt hướng

Một xưởng gốm yên tĩnh màu men ngọc trên nền xám tro, tiêu đề có chân mềm, hoạ tiết vòng bàn
xoay. Khác starter: (1) tiêu đề serif Lora, (2) hoạ tiết vòng đồng tâm thay vòng tròn mờ,
(3) số chỗ còn lại thành "nhãn lò".
