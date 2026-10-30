# 01-landing: Đất Nung

Cỡ việc M, web marketing một trang. Hướng thị giác: `CHƯA DUYỆT` (benchmark, không có người quyết định).

## Khung vấn đề

- Người dùng: 22–35 tuổi, đến từ Instagram, mở trên điện thoại, chưa từng làm gốm.
- Việc chính: hiểu một buổi học có gì, giá bao nhiêu, rồi đặt chỗ.
- Bối cảnh: đang lướt điện thoại, vội vừa phải; sợ "không biết làm", sợ đặt nhầm ngày, sợ tốn tiền không rõ.
- Kết quả quan sát được: một lượt đặt chỗ có lớp, ngày (thứ + ngày tháng), ca, số người, tổng tiền.

## Kế hoạch thị giác (CRAFT.md mục 1)

```text
Ngành và vật gốc:      xưởng gốm; vật gốc là vòng xoay bàn xoay + vệt men ngọc chảy trên thân cốc
Một câu cảm giác:      "mát, chậm, tay nghề: như một chiếc cốc men ngọc còn hằn vòng xoay"
Chữ:                   tiêu đề Source Serif 4 600, 34/1.15 (390) đến 56/1.08 (1280), tracking -1.5%;
                       thân Be Vietnam Pro 400, 17/1.6; nhãn 500/600; có tiếng Việt: có (cả hai có ₫)
Màu theo vai trò:      nền #eef1ec (sứ mộc xám xanh), bề mặt #fbfcfa, chữ #1b211e,
                       thương hiệu #2f5b4e (men ngọc đậm), nhấn: không thêm; màu đất #b07a52 chỉ trong hình vẽ
Hình khối:             bo card 14px, control dạng viên (999px); viền mảnh 1px thay bóng; nét 1.75px
Bố cục màn chính:      [Đất Nung                                ]
                       [H1 câu định vị        | SVG cốc trên bàn xoay ]
                       [3 dữ kiện + Đặt chỗ   |                        ]
                       [Ba lớp (bảng dòng)    | Lịch + giá đã gồm      ]
                       [Một buổi học (3 vòng) | Câu hỏi thường gặp     ]
                       [Card men ngọc: giá từ, lịch, nút trắng Đặt chỗ ]
                       [Địa chỉ, điện thoại                            ]
Lưới và mật độ:        390: 1 cột, lề 20; 1280: 12 cột gutter 24, nội dung tối đa 1120; mật độ vừa;
                       mỗi hàng desktop chia 7/5 hoặc 5/7 để không còn cột hẹp lọt thỏm
Card nổi bật:          một duy nhất ở cuối trang: nhãn "Lớp cuối tuần"; chính "Từ 300.000 ₫";
                       ngữ cảnh "Thứ Bảy và Chủ nhật, 9:00 và 14:00" + nút trắng Đặt chỗ
Một điểm táo bạo:      hình SVG cốc men ngọc trên bàn xoay với các vòng đồng tâm ở hero
Ba điểm khác starter:  1. chữ có chân Source Serif 4 cho tiêu đề và giá
                       2. màu men ngọc + nền sứ thay navy/xám lạnh; bo 14px thay 24px
                       3. "Một buổi học" vẽ thành ba vòng xoay lớn dần thay danh sách số
Đã đối chiếu mục 2:    - "nền kem + đất nung" gần chạm (ngành gốm): đổi sang nền sứ xám xanh + men ngọc,
                         màu đất chỉ ở thân cốc trong hình
                       - hero căn giữa: dùng bố cục lệch chữ trái, hình phải
                       - ba card icon giống nhau cho ba lớp: dùng bảng dòng trong một card
                       - eyebrow IN HOA: không dùng
```

## Dấu ấn (SIGNATURE.md)

Vật gốc: vòng xoay bàn xoay. Cần gạt đã đổi: hình khối (bo 14px, control viên), chữ tiêu đề
(Source Serif 4), cách thể hiện số liệu (giá chữ có chân, bước học là vòng đồng tâm lớn dần),
hoạ tiết card nổi bật (vòng đồng tâm mờ ở góc phải, không chạm vùng chữ).

## Luồng đặt chỗ

Hai nút "Đặt chỗ" (hero, card cuối trang) mở cùng hộp thoại `#booking`.

1. Form: Lớp (3 lựa chọn, giá + thời lượng) → Ngày (4 ngày cuối tuần tới, "Thứ Bảy 31/10") →
   Ca (Sáng 9:00, Chiều 14:00, kèm số chỗ còn) → Số người (bước 1..sức chứa lớp) → Họ tên, Điện thoại.
2. Nút "Đặt chỗ" của form khoá khi thiếu dữ liệu; lý do hiện ngay cạnh nút (`aria-describedby`):
   Chọn lớp / Chọn ngày / Chọn ca / Ca này còn N chỗ / Nhập họ tên / Nhập số điện thoại / Kiểm tra số điện thoại.
3. Bấm "Đặt chỗ" → hộp xác nhận tiêu đề "Đặt chỗ": lớp, ngày, ca, số người × giá, liên hệ, tổng tiền;
   nút "Hủy" (về form, giữ dữ liệu) và "Đặt chỗ".
4. Kết quả "Đã đặt chỗ" + mã đặt chỗ + tóm tắt + tổng; "Xong" đóng hộp thoại. Trang hiện thẻ trạng thái
   lượt vừa đặt cạnh cả hai nút; số chỗ còn của ca đó giảm khi mở lại form.
5. Đóng (X hoặc Esc) giữa chừng: giữ bản nháp, mở lại thấy nguyên lựa chọn.

Nhánh lỗi: số điện thoại sai định dạng → lỗi tại ô + lý do ở nút → sửa thì mở khoá.
Số người vượt chỗ còn → lý do "Ca này còn N chỗ" → giảm số người thì mở khoá. Ca hết chỗ bị khoá, nhãn "Hết chỗ".

## Phần mô phỏng / dữ liệu mẫu (không hiện trên trang)

- Không có backend. Số chỗ còn mỗi ca được sinh cố định trong JS từ sức chứa trong đề trừ đi một số
  đã đặt giả định; ca "Bàn xoay cơ bản, thứ Bảy đầu tiên, 9:00" cố ý hết chỗ để có trạng thái khoá.
- Ngày được tính từ ngày mở trang: 4 ngày thứ Bảy/Chủ nhật kế tiếp (không tính hôm nay).
- Mã đặt chỗ sinh tại chỗ (DN-ngày-số), không gửi đi đâu.
- Hình minh hoạ là SVG tự vẽ trong trang; không ảnh chụp.
- Icon lấy từ `design-system/components/icons.svg` và `starter/icons-app.svg`, nhúng inline.

## Kiểm luồng (FLOW.md)

Xem kết quả chạy ở báo cáo giao. Kịch bản Playwright: `scenarios.cjs`.
