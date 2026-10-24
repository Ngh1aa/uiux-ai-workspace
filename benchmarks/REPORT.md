# Kết quả bộ đề chuẩn

Sinh tự động bởi `python3 benchmarks/report.py`. Không sửa tay.

Điểm rubric từ 1 tới 5 theo [quality-bar-rubric](../skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md).
Cột *Soát* là số lỗi và cảnh báo của `taste-check` trên 390px, 1024px và 1280px, sáng và tối.

| Lần chạy | Đề | Cỡ | Lỗi soát | Cảnh báo | Hard fail | TB | Thấp nhất | Ngưỡng |
|---|---|---|---|---|---|---|---|---|
| 2026-10-24-v1 | 01-landing | M | 0 | 0 | 0 | 3.7 | 3 (Chữ, Tương tác, phản hồi, Tay nghề, dấu ấn) | Đạt |
| 2026-10-24-v1 | 02-app | L | 0 | 0 | 0 | 3.8 | 3 (Tương tác, phản hồi, Tay nghề, dấu ấn) | Chưa đạt |
| 2026-10-24-v1 | 03-dashboard | M | 0 | 0 | 1 | 3.8 | 3 (Tương tác, phản hồi, Tay nghề, dấu ấn) | Chưa đạt |

## Ghi chú từng lần chạy

- **2026-10-24-v1** (agent-heuristic, repo `cc0276e`): Mốc gốc. Landing và dashboard đạt mức điểm M nhưng dashboard có hard fail thiếu trạng thái dữ liệu; app chưa đạt ngưỡng L vì tương tác mỏng và nhìn vẫn là starter kit đổi màu. Người chấm cũng là người làm, nên điểm có thể cao hơn thực tế.
