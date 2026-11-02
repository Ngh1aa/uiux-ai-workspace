# Đề 6: Dashboard phân tích cho chuỗi trà sữa "Mây"

**Thêm vào:** 2026-11-02

**Cỡ việc:** M (một trang phân tích, có bộ lọc). **Ngưỡng rubric:** không hard fail, trung bình ≥ 3.5,
không chiều nào < 3.

## Bối cảnh

Mây có 4 cửa hàng ở TP.HCM. Quản lý vùng mở trang này mỗi sáng thứ Hai trên máy tính, đôi khi xem lại trên
điện thoại, để quyết định tuần này dồn nhân sự và khuyến mãi vào cửa hàng nào.

**Câu hỏi chính:** *Cửa hàng nào đang tụt, tụt ở đâu, và tuần này cần làm gì?*

## Dữ liệu (dùng đúng)

- Kỳ mặc định: tuần 26/10–01/11/2026, so với tuần 19/10–25/10/2026.
- Doanh thu tuần (triệu đồng), tuần này / tuần trước:
  | Cửa hàng | Tuần này | Tuần trước | Số ly | Đánh giá trung bình |
  |---|---|---|---|---|
  | Quận 1 | 182 | 176 | 4.210 | 4,6 |
  | Quận 3 | 141 | 168 | 3.380 | 4,1 |
  | Bình Thạnh | 129 | 131 | 3.050 | 4,5 |
  | Thủ Đức | 96 | 88 | 2.410 | 4,4 |
- Quận 3, doanh thu theo ngày (triệu đồng), T2 → CN: 24, 23, 21, 15, 14, 22, 22. Tuần trước mỗi ngày
  khoảng 24.
- Quận 3, đánh giá 1–2 sao tuần này: 11 (tuần trước 3); 8 trong số đó nhắc "chờ lâu", vào T5 và T6.
- Quận 3, nhân sự ca tối T5 và T6: 2 người (lịch chuẩn 4).
- Cơ cấu doanh thu toàn chuỗi theo nhóm món: trà sữa 52%, trà trái cây 31%, cà phê 11%, khác 6%.

## Yêu cầu

- Bộ lọc kỳ (tuần này, 4 tuần, tháng) áp dụng cho cả trang, luôn nhìn thấy; đổi kỳ thì mọi panel đổi theo.
- Bấm một cửa hàng mở phần chi tiết của cửa hàng đó (drill-down), có đường quay lại tổng quan và giữ kỳ đã chọn.
- Có ít nhất: so sánh 4 cửa hàng, xu hướng theo ngày của cửa hàng đang xem, cơ cấu nhóm món.
- Việc cần xử lý (Quận 3 tụt, ca tối thiếu người) phải nổi bật trước, không đỏ cả trang.
- Trạng thái tải, lỗi theo từng panel: có một nút hoặc tham số để xem panel đánh giá ở trạng thái lỗi
  mà các panel khác vẫn hiện số.
- Đọc tốt ở 1024px, 1280px, 1440px và 390px, sáng và tối, không cuộn ngang.
- Theo `TASTE.md` (mục "Dashboard") và skill `data-visualization-and-dashboard-ux`.

## Giao

Một file `06-analytics-dashboard/index.html` trong thư mục lần chạy.
