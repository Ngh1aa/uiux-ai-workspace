# Craft thị giác cho dashboard

Đọc khi dựng hoặc sửa một dashboard. [`SKILL.md`](../SKILL.md) nói cái gì phải đúng; file này nói
làm sao cho đẹp và dễ quét. Mục "Dashboard" trong [`TASTE.md`](../../../TASTE.md) đứng trên file này.
Ca thật: [Nova Home](nova-dashboard-case.md).

## 1. Thứ tự đọc

- Hàng đầu trả lời câu hỏi chính của màn (ví dụ "tiêu được bao nhiêu", "hôm nay gửi đơn nào").
- Ngay sau đó là việc cần xử lý: cảnh báo, quá hạn, giao dịch lạ. Đặt thành một dải hoặc panel riêng
  có nút đi thẳng tới việc đó, không để nó là một dòng lẫn trong danh sách "Gần đây".
- Số tham khảo (tổng hợp tháng, phân bổ chi tiêu, tiến độ mục tiêu) xuống dưới.
- Không có việc cần xử lý thì dải đó biến mất, không để "0 cảnh báo".

## 2. Giải phẫu panel

| Phần | Quy tắc |
|---|---|
| Tiêu đề | Danh từ ngắn hoặc câu trả lời ("Còn 1.050 vào 27/9"). Không dòng mô tả dưới tiêu đề |
| Chip kỳ | "Tháng 9", "15–30/9", "7 ngày". Phải khớp đúng khoảng mà biểu đồ vẽ |
| Số chính | Một số lớn, chữ số tabular, đơn vị đi liền |
| So sánh | Dấu + hoặc −, mũi tên, và cơ sở: "+12% so với tháng 8". Với chi tiêu, tăng là xấu: dùng màu trung tính hoặc cảnh báo, không xanh |
| Biểu đồ | Một thông điệp, một điểm nhấn |
| Hành động | Một liên kết hoặc nút dẫn tới việc làm tiếp ("Xem giao dịch", "Chuyển vào quỹ") |

KPI tile: nhãn 13–14 px, số 28–36 px, so sánh 12–13 px. Không quá 4 tile một hàng.

## 3. Trình bày biểu đồ

- **Màu.** Series dùng token `dataviz` của design system. Một series: màu thương hiệu. Hai series
  so sánh: thương hiệu và xám trung tính, không hai màu rực. Màu trạng thái (đỏ, hồng cảnh báo, cam)
  không làm màu dữ liệu.
- **Một điểm nhấn.** Cột hôm nay, cột cao nhất hoặc điểm thấp nhất đậm màu; các cột khác nhạt
  (cùng sắc, độ sáng cao hơn). Nhãn số đặt ở điểm nhấn và ở các cột cần đọc.
- **Cột.** Rộng 40–60% ô; bo góc trên 4 px; trục giá trị từ 0; giá trị 12 px trên đầu cột hoặc cuối
  thanh ngang. Quá 6 nhóm trên màn hẹp: chuyển sang thanh ngang.
- **Đường.** Nét 2 px, chấm ở điểm cuối kèm nhãn giá trị. Vùng tô dưới đường thì tô từ 0, hoặc bỏ tô.
  Đường tham chiếu (mục tiêu, buffer) nét đứt, ghi nhãn ngay đầu đường.
- **Lưới.** Tối đa 3 đường lưới ngang, 1 px, rất nhạt. Không khung trục đậm.
- **Nhãn trực tiếp.** Tên series đặt ở cuối đường hoặc đầu dòng thanh. Không chú giải ô màu.
- **Tên cho trình đọc màn hình.** `role="img"` và `aria-label` nêu kết luận có số, hoặc
  `figure` + `figcaption`. Biểu đồ quan trọng có thêm bảng hoặc danh sách giá trị.

## 4. Thay thế hay dùng

| Đang có | Thay bằng |
|---|---|
| Donut 4 phần trở lên | Thanh ngang xếp giảm dần: tên, thanh, số tiền, % ở cuối. Gom phần nhỏ vào "Khác" |
| Vòng % cho một mục tiêu | Số lớn "64%" + thanh tiến độ ngang + "còn 1.800" |
| Cột đôi thu/chi có chú giải | Hai thanh ngang có nhãn "Thu", "Chi" và số ở cuối; hoặc một cột chênh lệch |
| Gauge, đồng hồ tốc độ | Bullet chart hoặc số + thanh có vạch mục tiêu |
| Biểu đồ không có giá trị nào | Nhãn số ở điểm nhấn, hoặc câu tóm tắt có số dưới biểu đồ |

## 5. Lưới panel

- Từ 1024 px dùng lưới 12 cột. Ghép panel theo chiều cao nội dung: panel dài (danh sách 5 dòng) đi
  với panel dài, panel ngắn đi với panel ngắn.
- Không để hàng kéo giãn panel ngắn thành khoảng trống đáy (`panel-void`). Cách sửa, theo thứ tự:
  đổi span, chuyển panel sang hàng khác, ghép hai panel ngắn thành một cột, thêm nội dung có ích.
  Không dùng `align-items: start` để giấu: panel lệch đáy vẫn là lưới lệch.
- Hàng cuối không có panel lẻ (`panel-orphan`): cho panel trải hết hàng, hoặc chia lại lưới.
- Kiểm ở 1024, 1280 và 1440: lưới đẹp ở 1440 thường vỡ ở 1024.

## 6. Mobile

- Giữ đúng thứ tự đọc của mục 1; không đẩy cảnh báo xuống dưới các panel lớn.
- Tối đa 4 panel đầy đủ. Các panel tham khảo còn lại thu thành dòng tóm tắt: tiêu đề, số chính,
  chevron mở màn chi tiết.
- Biểu đồ xu hướng thu thành sparkline kèm số đầu và số cuối. Cột dọc quá 6 nhóm chuyển sang ngang.
- Không bảng nhiều cột: mỗi dòng thành một khối hai tầng (tên và số; phụ và trạng thái).

## 7. Trạng thái từng panel

- Đang tải: khung xương đúng hình panel, tiêu đề vẫn hiện; panel khác vẫn dùng được.
- Rỗng: một câu nêu vì sao rỗng và một hành động.
- Lỗi: câu lỗi, nút "Thử lại", số liệu tốt gần nhất nếu có.
- Dữ liệu cũ quá hạn: chip trạng thái "Chưa cập nhật từ 09:42" ở panel chính.
- Không thay cả `main` bằng một màn lỗi khi chỉ một nguồn dữ liệu hỏng.

## 8. Đánh dấu cho checker

`taste-check.cjs` tự nhận biểu đồ (canvas, SVG có đường/cột/vòng, `[role="img"]` có vạch, donut
`conic-gradient`). Khi biểu đồ vẽ theo cách khác, thêm `data-chart` để checker soát. Vùng trống có
chủ đích đánh dấu `data-whitespace`. Lớp `risk`, `danger`, `error`, `alert`, `warning`, `overdue`,
`unusual` hoặc `data-status` cho checker biết màu nào là màu trạng thái.

```sh
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs "app.html?screen=home" \
  --width 390 --width 1024 --width 1440 --layout strict
```
