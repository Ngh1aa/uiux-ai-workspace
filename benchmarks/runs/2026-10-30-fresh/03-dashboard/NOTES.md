# 03-dashboard: Kho Len Nhỏ

Cỡ M, track Web app / dashboard. Hướng thị giác: `CHƯA DUYỆT` (đề chuẩn, không có người quyết định;
đi tiếp với hướng đề xuất duy nhất dưới đây, không dựng 2–3 hướng vì giới hạn thời gian).

## Khung vấn đề

- Người dùng: chủ shop tự quản lý kho, mở trang mỗi sáng trên máy tính, đôi khi trên điện thoại.
- Câu hỏi chính: hôm nay nhập hàng gì và gửi đơn nào trước?
- Thứ tự đọc: card nổi bật (đơn chờ gửi, đơn gửi trước, số cần nhập) → bảng sắp hết hàng → đơn quá hạn → doanh thu 7 ngày.

## Kế hoạch thị giác (CRAFT.md)

```text
Ngành và vật gốc:      bán lẻ len và dụng cụ đan móc online; vật gốc: cuộn len và đường may chần (đường khâu nét đứt)
Một câu cảm giác:      gọn, ấm, thủ công, như sổ kho viết tay của tiệm len nhỏ
Chữ:                   tiêu đề Source Serif 4 600, 28/22/18px; số lớn Source Serif 4 600 56px tabular;
                       thân Be Vietnam Pro 15px, line-height 1.55; có tiếng Việt: có (cả hai font có bộ Việt)
Màu theo vai trò:      nền #f5f3f5, bề mặt #ffffff, chữ #1e1a1d, thương hiệu #7a2f5c (dâu tằm),
                       nhấn trạng thái: amber (đủ bán ≤ 2 ngày), đỏ chỉ trong chip "Quá N ngày"
Hình khối:             bo 12px card, 10px control, 16px hộp thoại; viền 1px nhạt, không bóng
Bố cục màn chính:      [header: Len Nhỏ                         Thứ Sáu, 30/10/2026]
                       [h1 Việc kho hôm nay]
                       [card nổi bật 12 cột: Đơn chờ gửi 14 | gửi trước #2041 | 3 chỉ số]
                       [Sắp hết hàng: bảng 7 cột      ][Đơn quá hạn gửi: 3 dòng 5 cột]
                       [Doanh thu 7 ngày (nghìn đồng): cột, tổng 18.550     12 cột    ]
Lưới và mật độ:        390: 1 cột, bảng chuyển thành dòng xếp chồng; 1280: lưới 12 cột, gutter 24, mật độ vừa;
                       biểu đồ trải hết hàng cuối để không có mảng trống
Card nổi bật:          nhãn "Đơn chờ gửi"; số chính 14; ngữ cảnh: "Gửi trước: #2041 chị Hà" + 3 chỉ số
                       (quá hạn gửi, cần nhập gấp, sắp hết hàng)
Một điểm táo bạo:      đường khâu nét đứt chạy quanh mép trong card nổi bật (outline dashed, cách mép 8px,
                       chữ cách đường khâu 16px nên không đè chữ) + số 14 serif lớn
Ba điểm khác starter:  1. màu dâu tằm thay navy, nền trung tính hơi tím 2. tiêu đề và số serif (Source Serif 4)
                       3. bo 12px thay 24px, card có viền mảnh, hoạ tiết đường khâu
Đã đối chiếu mục 2:    tránh nền kem + đất nung (dùng dâu tằm trên nền xám tím); không eyebrow IN HOA;
                       không thanh màu trái (trạng thái bằng chip + icon); không chú giải biểu đồ (nhãn giá trị
                       trực tiếp trên cột, đơn vị trong tiêu đề); không " · "
```

## Quyết định dataviz

- Cột dọc, 7 kỳ rời rạc, trục giá trị bắt đầu từ 0 (chiều cao cột = giá trị / 4.500).
- Một chuỗi, một màu, nhãn giá trị trên đầu cột nên không cần chú giải hay lưới (lưới bỏ để không đè chữ).
- Đơn vị "nghìn đồng" trong tiêu đề; tổng 18.550 cạnh tiêu đề. Nhãn ngày kèm thứ và ngày tháng.
- Biểu đồ là danh sách `<ol>` có chữ thật (thứ, ngày, giá trị) nên trình đọc màn hình đọc được, không cần bảng ẩn.
- Không hiện dòng nguồn/thời điểm cập nhật trên màn (TASTE). Trạng thái tải/lỗi/rỗng của panel: không dựng
  trong bản này vì không có backend; FAIL theo dashboard-gate mục "Last-updated" và "states per panel" là
  quyết định có chủ ý theo TASTE và giới hạn bản mẫu.

## Hành vi (JS trong trang, không backend)

- Ghi nhập hàng (mỗi dòng sản phẩm): hộp thoại cùng tên "Ghi nhập hàng", ô số lượng; nút xác nhận khoá kèm lý do
  (aria-describedby) khi trống hoặc ngoài 1–999; xem trước "Sau khi nhập" (còn, đủ bán). Xác nhận → dòng cập nhật
  còn/đủ bán/chip, card nổi bật cập nhật "cần nhập gấp", "sắp hết hàng"; thẻ kết quả có Hoàn tác.
- Gửi đơn (mỗi đơn quá hạn): hộp thoại "Gửi đơn" có Hủy, hiện mã đơn, khách, nơi nhận, số ngày quá hạn.
  Xác nhận → đơn rời danh sách, đơn chờ gửi 14 → 13, quá hạn 3 → 2, "Gửi trước" chuyển sang đơn kế tiếp;
  hết đơn thì hiện trạng thái rỗng. Thẻ kết quả có Hoàn tác (trả đơn về đúng vị trí và số cũ).
- Hủy / Esc đóng hộp thoại, focus về nút đã mở.
- "Sắp hết hàng" = đủ bán ≤ 7 ngày; "cần nhập gấp" = đủ bán ≤ 2 ngày. Đủ bán = làm tròn xuống (còn / bán mỗi ngày).

## Dữ liệu

Toàn bộ số liệu lấy đúng từ đề (dữ liệu minh hoạ, không phải shop thật). Ngày hôm nay giả định Thứ Sáu 30/10/2026;
7 ngày qua là T6 23/10 đến T5 29/10. Đơn vị "bán mỗi ngày" (cuộn/cây) suy từ cột "Còn".

## Kiểm

- static-check, flow-check (prototype): xem báo cáo cuối.
- scenarios.cjs: viết cho Playwright, máy này không có trình duyệt nên CHƯA CHẠY (UNKNOWN).
- Render 390/1280, sáng/tối: UNKNOWN (không có trình duyệt). check-brand.py: xem báo cáo.
- Icon: bộ `design-system/components/icons.svg`, nhúng bằng inline-icons.py.
