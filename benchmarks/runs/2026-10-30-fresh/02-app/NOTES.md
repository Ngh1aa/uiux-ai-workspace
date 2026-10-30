# 02-app: Cầu Lông Gần Nhà, ghi chú bàn giao

Cỡ việc L, làm theo lượt benchmark fresh 2026-10-30. Hướng thị giác: `CHƯA DUYỆT` (không có người
quyết định trong lượt này; đi thẳng với hướng đề xuất dưới đây, không dựng 2–3 hướng so sánh do giới hạn thời gian).

## Kế hoạch thị giác (CRAFT.md mục 1)

```text
Ngành và vật gốc:      sân cầu lông cộng đồng; vật gốc: vạch kẻ sân trên thảm xanh (phụ: bảng tỉ số, lưới)
Một câu cảm giác:      "gọn, nhanh, sáng sủa như mặt sân vừa kẻ vạch, chạm hai lần là có sân"
Chữ:                   tiêu đề và số giờ Manrope 700 (24–40px, tabular-nums, kiểu bảng tỉ số);
                       thân Be Vietnam Pro 15–17px, line-height 1,5; có tiếng Việt: có (cả hai có ₫)
Màu theo vai trò:      nền #f2f4f1, bề mặt #ffffff, chữ #141a17, thương hiệu #106b52 (xanh thảm sân),
                       nhấn = chính màu thương hiệu, lỗi dùng token danger của design system;
                       tối: nền #0f1412, bề mặt #18201c, thương hiệu #17573f, nút #7fd3b0
Hình khối:             bo 12px cho mọi card (cứng như mép sân), control 10px, sheet 20px; phẳng, không bóng, không viền card
Bố cục màn chính:      Trang chủ
                       [ Chào Minh / Thứ Năm 23/10            ]
                       [ CARD NỔI BẬT: Lượt sắp tới | 18:00–19:00 | ngày | sân, sân số | Xem lịch ][sơ đồ sân]
                       [ Tối nay gần bạn               Xem tất cả ]
                       [ 3 dòng sân: tên, cách, khung trống  > ]
                       [ thanh tab nổi: viên đang chọn + 2 icon ]
Lưới và mật độ:        390: một cột, lề 20; mật độ vừa. 1280: gallery 5 khung xếp hàng ngang, tự xuống dòng
Card nổi bật:          nhãn "Lượt sắp tới"; chính "18:00–19:00" cỡ 40; ngữ cảnh ngày + sân + sân số, nút trắng "Xem lịch"
Một điểm táo bạo:      giờ lượt đặt cỡ lớn Manrope cạnh sơ đồ sân vạch trắng, ô sân đã đặt được tô
Ba điểm khác starter:  1. bo 12px thay 24px  2. font số Manrope kiểu bảng tỉ số  3. sơ đồ vạch sân trong card nổi bật
                       (nằm cột riêng, không đè chữ) và ô khung giờ như ô bảng giờ sân
Đã đối chiếu mục 2:    không navy; không nền kem đất nung; không eyebrow IN HOA; không gradient; không " · ";
                       không thanh màu trái; một card nổi bật duy nhất (trang chủ)
```

## Cấu trúc và điều hướng

- 5 khung 390 × 844 có `data-screen`, đặt cạnh nhau (gallery). Nhãn tên màn ngắn nằm trong `[data-annotation]`
  ngoài khung. Bấm trong khung sẽ cuộn tới khung đích và cập nhật nội dung khung đó (đúng sân, đúng khung giờ).
- Tab (Trang chủ, Tìm sân, Lịch của tôi) có thanh tab nổi. Chi tiết sân và Đặt sân là màn con: Back trên appbar,
  không thanh tab. Back về đúng khung vừa rời (ghi `cameFrom` cho từng khung khi điều hướng vào); không có lịch sử
  thì về cha mặc định (Chi tiết → Tìm sân, Đặt sân → Chi tiết).
- Đặt sân: chọn khung ở Chi tiết → Tiếp tục → form (khung giờ có sheet chọn riêng, số người, ghi chú, tổng tiền) →
  "Đặt sân" mở sheet xác nhận có Hủy → kết quả "Đã đặt sân" → Xem lịch → Lịch của tôi, tab Sắp tới có lượt mới
  (lượt mới gắn "Mới đặt"); trang chủ đổi card nổi bật sang lượt gần nhất; số khung trống ở danh sách giảm.
- Lỗi: đặt Sân Kỳ Hoà 19:00 lần đầu luôn trả "vừa có người đặt" (mô phỏng tranh chấp). Form xoá khung đã chọn,
  hiện banner lỗi kèm các khung còn trống của sân để chọn ngay, hoặc "Đổi khung" mở sheet; nút "Đặt sân" khoá kèm lý do
  (aria-describedby) tới khi chọn khung mới. Khung đặt hình Đặt sân ban đầu hiện sẵn trạng thái lỗi này để duyệt ảnh.
- Lịch của tôi ban đầu mở tab Đã qua để thể hiện trạng thái rỗng (đề yêu cầu): thẻ rỗng gọn, bên dưới là "Tối nay gần bạn"
  (3 sân của đề) để đặt tiếp ngay; đi từ "Xem lịch" thì mở Sắp tới.
- Thẻ sân (Trang chủ, Tìm sân, Lịch) có các khung trống tối nay là nút bấm được: mở Chi tiết đúng sân với khung đó chọn sẵn.

## Phần mô phỏng, dữ liệu mẫu

- Toàn bộ chạy bằng JS trong trang, không backend. "Hôm nay" giả định là thứ Năm 23/10 (lượt sẵn có là thứ Sáu 24/10).
- Tiện ích của Sân Kỳ Hoà và Sân Tân Định, khung đã đặt của từng sân ngoài dữ liệu đề, số sân được xếp cho lượt mới
  (sân số 2) là dữ liệu giữ chỗ.
- Icon: bộ của design system (`components/icons.svg`, `starter/icons-app.svg`), nhúng bằng `inline-icons.py`.
  Sơ đồ sân trong card nổi bật là SVG tự vẽ.

## Kiểm tra

- `check-brand.py brand.css`: ĐẠT, 0 lỗi.
- `static-check.cjs`: 0 lỗi. `flow-check.cjs --mode prototype`: tĩnh PASS, 0 FAIL, 0 WARN; UNKNOWN là nút JS tại chỗ và runtime, phủ bằng kịch bản.
- `scenarios.cjs`: 8/8 PASS trên Chromium 1243 sẵn trong máy (Playwright 1.63, trỏ `executablePath`), 0 lỗi JS trang.
  Hai nút khoá (`aria-disabled`) được bấm bằng `force: true` để chứng minh bấm vào không chuyển màn.
- `taste-check.cjs --width 390 --width 1024 --width 1280 --width 1440 --height 900 --reflow`, sáng và tối: 0 lỗi, 0 cảnh báo,
  không dùng `data-whitespace`. axe-core chưa cài nên chưa chạy.
- Đã xem ảnh: gallery 1280 và 1440 sáng; sheet chọn khung, sheet xác nhận, kết quả, Lịch có lượt mới, Trang chủ cập nhật ở sáng và tối.
- Chưa kiểm: trình đọc màn hình thật, chữ phóng 200%, thiết bị thật, người dùng thật; duyệt hướng `CHƯA DUYỆT`.
