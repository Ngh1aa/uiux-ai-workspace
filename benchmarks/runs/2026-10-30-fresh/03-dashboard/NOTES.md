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
Một điểm táo bạo:      đường khâu nét đứt quanh mép trong card nổi bật (outline dashed, outline-offset -8px,
                       nằm ngoài vùng chữ) + số 14 serif lớn
Ba điểm khác starter:  1. màu dâu tằm thay navy, nền trung tính hơi tím 2. tiêu đề và số serif (Source Serif 4)
                       3. bo 12px thay 24px, card có viền mảnh, hoạ tiết đường khâu
Đã đối chiếu mục 2:    tránh nền kem + đất nung (dùng dâu tằm trên nền xám tím); không eyebrow IN HOA;
                       không thanh màu trái (trạng thái bằng chip + icon); không chú giải biểu đồ (nhãn giá trị
                       trực tiếp trên cột, đơn vị trong tiêu đề); không " · "
```

## Quyết định dataviz

- Cột dọc, 7 kỳ rời rạc, trục giá trị bắt đầu từ 0 (chiều cao cột = giá trị / 5.000 của vùng cột).
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

## Kiểm (2026-10-30, Chromium headless có sẵn ở /opt/pw-browsers)

- static-check: ĐẠT, 0 lỗi 0 cảnh báo.
- flow-check --mode prototype: tĩnh PASS, 0 FAIL, 0 WARN; còn UNKNOWN runtime (đã kiểm bằng scenarios).
- check-brand.py brand.css: ĐẠT.
- taste-check --layout strict (390/1280, sáng/tối): 0 lỗi, 2 cảnh báo giữ lại: tên "Len cotton màu hồng đất"
  xuống dòng ở 390px cạnh chip đủ bán (tên sản phẩm dài thật, không cắt chữ).
  Đã sửa trước đó: hoạ tiết ::after bị báo đè chữ → đổi thành outline; nhãn chỉ số trong card nổi bật xuống dòng ở 390 → xếp dọc.
- scenarios.cjs: 9/9 PASS ở 1280×900 (chạy bằng script tạm ngoài repo), không lỗi JS.
- Đã nhìn ảnh 1280 và 390, sáng và tối, hộp thoại Ghi nhập hàng, trạng thái sau khi gửi hết đơn. Không cuộn ngang ở cả hai cỡ.
- Chưa kiểm: axe-core (không cài), trình đọc màn hình thật, thiết bị thật, người dùng thật.
- Dashboard gate: FAIL có chủ ý ở "last-updated/nguồn" (TASTE cấm dòng cập nhật/nguồn) và trạng thái tải/lỗi từng panel (không backend).
