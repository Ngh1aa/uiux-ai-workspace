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

## Sau khi sửa Nova bằng bản repo mới

Nhánh Nova `claude/home-dashboard-craft`, sửa tại nguồn `assets/nova-dashboard-v2.js` và
`assets/nova-ui/screens.css`, bundle chạy lại bằng generator. Ảnh: [1440](nova-case/after-1440.jpg),
[1024](nova-case/after-1024.jpg), [390](nova-case/after-390.jpg).

| Lỗi trước | Cách sửa |
|---|---|
| Giao dịch bất thường ở hàng ba | Panel "Needs your attention" ngay cạnh hero (desktop), ngay dưới hero (mobile); giữ nguyên `aria-label` mà test khoá |
| Donut 6 phần | Thanh ngang xếp theo giá trị, một màu trung tính, nhóm lớn nhất đậm, có số và % |
| Vòng 64% | Hai mục tiêu (Emergency buffer, Holiday Fund), mỗi mục số % + thanh ngang + "còn …" |
| Thu chi: chú giải, hồng trùng cảnh báo, "This month" trên Jan–Jun | Chip "Apr–Sep"; ô số "In/Out, September" có delta có cơ sở, chi tăng màu cảnh báo vàng; tháng hiện tại đậm, tháng trước nhạt; bỏ chú giải |
| Dòng phụ dưới "Balance forecast" | Bỏ; thêm nhãn trực tiếp "€500 buffer" trên đường nét đứt và chấm ở điểm thấp nhất |
| Lỗi nguồn dữ liệu làm trống cả trang | `?panel=forecast-error`: chỉ panel dự báo hiện lỗi và "Try again", các panel khác giữ số |
| Panel trống đáy, panel lẻ | Lưới theo vùng: 1 cột dưới 768, 2 cột tới 1399, 3 cột từ 1400; ghép panel theo chiều cao nội dung |
| Mobile 10 panel, dài 3.623px | 4 panel đầy đủ, 6 panel còn lại thành dòng tóm tắt mở đúng màn; dài 2.191px |

Giữ: ADN pastel iOS, câu chữ đã kiểm chứng với người dùng (kể cả ghi chú buffer), mọi URL và luồng.

Kiểm (02/11/2026, Chromium): `taste-check --layout strict` ở 390, 1024, 1280, 1440: 0 lỗi, không còn
cảnh báo dashboard; trạng thái lỗi panel cũng 0 lỗi. 57/57 test Playwright của Nova, a11y và browser
evidence trên các route Home đạt. `overlay-check`: 0 lỗi. Chưa kiểm: thiết bị thật, trình đọc màn hình
thật, người dùng thật.

Lần dựng lại này còn bắt được một lỗi của chính checker: chữ mực gần đen trên dòng cảnh báo bị nhận là
màu trạng thái. Đã sửa `status-series` và thêm test.
