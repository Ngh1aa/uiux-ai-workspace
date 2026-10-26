# Kết quả bộ đề chuẩn

Sinh tự động bởi `python3 benchmarks/report.py`. Không sửa tay.

Điểm rubric từ 1 tới 5 theo [quality-bar-rubric](../skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md).
Cột *Soát* là số lỗi và cảnh báo của `taste-check` trên 390px, 1024px và 1280px, sáng và tối.
Lượt sửa tiếp đo khả năng cải tiến mẫu có sẵn; chỉ lượt làm mới mới dùng để đánh giá chất lượng bản đầu.
Review độc lập là khai báo về người chấm; agent độc lập vẫn là heuristic, không phải người dùng thật.

| Lần chạy | Kiểu lượt | Review độc lập | Đề | Cỡ | Lỗi soát | Cảnh báo | Hard fail | TB | Thấp nhất | Ngưỡng |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-24-v1 | Chưa rõ | Không | 01-landing | M | 0 | 0 | 0 | 3.7 | 3 (Chữ, Tương tác, phản hồi, Tay nghề, dấu ấn) | Đạt |
| 2026-10-24-v1 | Chưa rõ | Không | 02-app | L | 0 | 0 | 0 | 3.8 | 3 (Tương tác, phản hồi, Tay nghề, dấu ấn) | Chưa đạt |
| 2026-10-24-v1 | Chưa rõ | Không | 03-dashboard | M | 0 | 0 | 1 | 3.8 | 3 (Tương tác, phản hồi, Tay nghề, dấu ấn) | Chưa đạt |
| 2026-10-24-v2 | Sửa tiếp | Không | 01-landing | M | 0 | 0 | 0 | 3.9 | 3 (Chữ) | Đạt |
| 2026-10-24-v2 | Sửa tiếp | Không | 02-app | L | 0 | 0 | 0 | 4.0 | 4 (mọi chiều) | Đạt |
| 2026-10-24-v2 | Sửa tiếp | Không | 03-dashboard | M | 0 | 0 | 0 | 4.0 | 4 (mọi chiều) | Đạt |

## Ghi chú từng lần chạy

- **2026-10-24-v1** (agent-heuristic, repo `cc0276eb89c4317a443f95cae30f66906d00fecf`): Mốc gốc. Landing và dashboard đạt mức điểm M nhưng dashboard có hard fail thiếu trạng thái dữ liệu; app chưa đạt ngưỡng L vì tương tác mỏng và nhìn vẫn là starter kit đổi màu. Người chấm cũng là người làm, nên điểm có thể cao hơn thực tế.
- **2026-10-24-v2** (agent-heuristic, repo `UNKNOWN`): Sau vòng cải tiến 1 (mẫu trạng thái web, hướng dẫn dấu ấn, mẫu chọn nhanh và thanh tổng tiền). Cả ba đề đạt ngưỡng; chiều tương tác và dấu ấn lên từ 3 thành 4. Sửa tiếp từ bản v1 chứ không làm lại từ đầu, và người chấm vẫn là người làm.
