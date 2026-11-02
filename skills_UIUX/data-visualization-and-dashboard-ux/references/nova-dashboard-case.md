# Ca thật: Nova Home (dashboard ngân hàng, 02/11/2026)

Nova là prototype ngân hàng cá nhân (repo `Ngh1aa/Nova`), màn Home là dashboard chính: số tiêu được trong
14 ngày, dự báo số dư, hóa đơn sắp tới, giao dịch, thu chi, chi tiêu theo nhóm, tiến độ quỹ. Ca này dùng
làm bài test thật cho skill dashboard, sau khi bài benchmark kho len qua mọi checker mà chủ repo vẫn chê.

Ảnh trước khi sửa (commit Nova `35b93ae`): [1440](nova-case/before-1440.jpg),
[1024](nova-case/before-1024.jpg), [390](nova-case/before-390.jpg).

## Điểm làm tốt, nên học

- Hero trả lời đúng câu hỏi chính ("Safe to spend for the next 14 days"), có so sánh có cơ sở
  ("€124 more than last week") và hai hành động.
- Biểu đồ dự báo có đường buffer nét đứt và câu kết luận có số ("Lowest point €1,050 on 27 Sep…"),
  `aria-label` nêu kết luận.
- Một họ chữ hệ thống, chữ số tabular, ADN pastel iOS nhất quán.

## Chấm theo dashboard gate (trước khi sửa)

| Mục | Kết quả | Bằng chứng |
|---|---|---|
| Panel có câu hỏi và hành động | FAIL | "Money in and out", "Spending by category", "Your card" chỉ trình bày số |
| Thứ tự theo việc cần xử lý | FAIL | "Unusual card activity", điểm vào của luồng chính, nằm hàng thứ ba ở 1440 (y≈916) |
| Delta có cơ sở và chiều tốt/xấu | FAIL một phần | "Money out 8% more than last month" không dấu, không cho biết tăng là xấu |
| Kỳ khớp biểu đồ | FAIL | Chip "This month" trên biểu đồ cột Jan–Jun |
| Trục cột/vùng từ 0 | UNKNOWN | Không có trục giá trị |
| Không mã hoá chỉ bằng màu | FAIL | Thu/chi và 6 nhóm chi tiêu chỉ phân biệt bằng ô màu chú giải |
| Donut ≤ 3 phần | FAIL | Donut 6 phần; vòng 64% làm gauge |
| Màu trạng thái riêng | FAIL | Hồng "Expenses" cùng sắc hồng cảnh báo của "Unusual card activity" |
| Trạng thái từng panel | FAIL | `nova-native-states.js` thay cả `main` bằng một màn Empty/Loading/Error |
| Tóm tắt chữ / giá trị | FAIL một phần | Chỉ biểu đồ dự báo có kết luận; cột thu chi không có giá trị nào |
| Lưới cân | FAIL | 1440: "Upcoming bills" trống đáy 200px, "Savings progress" trống 179px; 1024: "Savings progress" lẻ hàng cuối |

## Checker cũ bắt được gì

`taste-check --layout strict` trước 02/11 chỉ báo: danh sách giao dịch tràn ngang 12px, nhãn tab
10,5px, vùng chạm 32px, một dòng phụ dưới tiêu đề. Không mục nào ở bảng trên. Checker cũng không
nhận `app.html?screen=home`. TASTE cấm giờ cập nhật và chú giải trong khi skill bắt buộc, nên agent
có cớ ghi "FAIL có chủ ý".

## Đã đổi trong repo

- TASTE mục "Dashboard": việc cần xử lý đứng trước; kỳ trong tiêu đề, giờ cập nhật một chỗ; nhãn
  trực tiếp; màu trạng thái riêng; donut ≤ 3 phần; panel cân hàng.
- `taste-check`: `chart-donut`, `chart-name` (lỗi); `chart-gauge`, `chart-values`, `chart-legend`,
  `status-series` (cảnh báo); `panel-void`, `panel-orphan` (bố cục, lỗi khi strict); nhận query string.
  Trên Nova Home trước khi sửa, các luật mới báo đúng mọi mục FAIL đo được bằng DOM ở bảng trên.
- [Trần điểm dashboard](../../design-critique-and-rationale/references/dashboard-caps.md) cho rubric.
- [dashboard-craft.md](dashboard-craft.md): thứ tự đọc, giải phẫu panel, trình bày biểu đồ, thay thế,
  lưới, mobile, trạng thái từng panel.

Phần còn phải soát bằng mắt: panel có hành động hay không, chiều tốt/xấu của delta, kỳ có khớp biểu đồ.
