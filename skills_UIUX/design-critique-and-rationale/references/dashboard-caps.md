# Trần điểm cho màn dashboard

Dùng cùng [quality-bar-rubric.md](quality-bar-rubric.md) khi chấm màn dashboard hay trang phân tích.
Rubric gốc giữ nguyên byte vì các review packet cũ trỏ vào nó; file này chỉ làm chặt thêm.

Lỗi dưới đây chưa sửa thì chiều tương ứng **tối đa 3**, dù phần còn lại đẹp đến đâu. Nguồn:
[ca Nova Home](../../data-visualization-and-dashboard-ux/references/nova-dashboard-case.md), nơi checker cũ
và điểm tự chấm 4/5 không bắt được lỗi dashboard.

| Lỗi | Trần ở chiều |
|---|---|
| Panel cần xử lý (cảnh báo, quá hạn) nằm dưới các panel tham khảo | 1. Task clarity |
| Chip kỳ không khớp khoảng biểu đồ vẽ; delta thiếu cơ sở hoặc chiều tốt/xấu | 1. Task clarity, 8. Content |
| `panel-void` hoặc `panel-orphan` ở bất kỳ bề rộng bắt buộc nào | 3. Layout & spacing |
| `chart-donut`, `chart-gauge`, `chart-legend` hoặc `chart-values` | 2. Hierarchy |
| `status-series` (màu trạng thái dùng làm màu dữ liệu) | 5. Colour & contrast |
| Một nguồn dữ liệu lỗi làm cả trang thành màn lỗi | 7. Interaction & feedback |

Mã luật lấy từ `taste-check.cjs`; xem [README công cụ QA](../../ui-craft-and-visual-qa/scripts/README.md).
