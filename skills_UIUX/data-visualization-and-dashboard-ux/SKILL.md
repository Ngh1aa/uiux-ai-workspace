---
name: data-visualization-and-dashboard-ux
description: Dashboard và biểu đồ. Dùng theo tác vụ được chọn trong WORKFLOWS.md.
---

# Dashboard và biểu đồ

Chọn cỡ/track theo [WORKFLOWS.md](../../WORKFLOWS.md). Mục "Dashboard" trong TASTE.md đứng trên file này.

1. Xếp panel theo việc cần xử lý: cảnh báo, quá hạn ở đầu (mobile cũng vậy), số tham khảo sau.
2. Mỗi panel trả lời một câu hỏi và dẫn một hành động; tiêu đề nói câu trả lời khi được.
3. Chọn biểu đồ theo tác vụ ([bảng chọn](references/practice-detail.md)). Donut tối đa 3 phần;
   một con số % dùng thanh ngang; cột có giá trị đọc được; nhãn trực tiếp, không chú giải ô màu.
4. Màu trạng thái chỉ cho trạng thái; dữ liệu dùng token `dataviz`. Mỗi biểu đồ nhấn một điểm.
5. Đơn vị và kỳ trong tiêu đề hoặc chip, khớp trục. Giờ cập nhật một chỗ ở panel chính.
6. Trạng thái tải, rỗng, cũ, lỗi theo từng panel; một panel lỗi không làm trống cả trang.
7. Lưới cân: không panel lẻ, không panel trống đáy. Mobile: tối đa 4 panel đầy đủ, còn lại thành dòng tóm tắt.

Sai: 18.550 không đơn vị/kỳ. Đúng: "Doanh thu 7 ngày (nghìn đồng)" với tổng 18.550.

Craft thị giác, chuyển đổi mobile và quy ước đánh dấu: [dashboard-craft](references/dashboard-craft.md).
Ca thật: [Nova Home](references/nova-dashboard-case.md). Chọn giữa hai biểu đồ, ma trận trạng thái:
[chart-selection-and-states](references/chart-selection-and-states.md). Toàn bộ hướng dẫn gốc:
[thực hành chuyên sâu](references/practice-detail.md).

Soát: `taste-check.cjs "<trang>" --layout strict` (luật `chart-*`, `status-series`, `panel-*`), rồi
[dashboard gate](checklists/dashboard-gate.md) với PASS / FAIL / UNKNOWN. Từ cỡ M áp dụng [FLOW.md](../../FLOW.md).
