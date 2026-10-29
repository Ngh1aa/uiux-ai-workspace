---
name: ux-structure-and-flow-design
description: Thiết kế cấu trúc UX trước thị giác: tác vụ, luồng, màn và trạng thái, điều hướng, khung dây và kiểm thử kịch bản.
---

# Cấu trúc UX và luồng

Đọc theo [WORKFLOWS.md](../../WORKFLOWS.md). Chuẩn hành vi nằm ở [FLOW.md](../../FLOW.md).

1. Viết việc chính, đối tượng và kết quả quan sát được; thiếu nghiên cứu ghi `HYPOTHESIS`.
2. Viết ba câu bối cảnh: ở đâu, vội thế nào, sợ hậu quả gì. Chuẩn bị chữ, số và trạng thái tiếng Việt thật trước khi chia khối.
3. Vẽ đường chính và nhánh lỗi/khôi phục; giữ deep link và điểm vào hợp lệ. Kiểm đúng đối tượng, quyền và Back.
4. Kiểm kê màn × trạng thái: câu hỏi khi vào, thông tin ưu tiên, hành động, đích, phản hồi, khôi phục.
5. Dựng khung dây theo nội dung, đi thử kịch bản; sửa blocker trước hướng thị giác.
6. Ghi `READY`, `READY_WITH_RISKS` hoặc `NOT_READY` cùng bằng chứng. Đây là đánh giá agent, không phải nghiên cứu người dùng.

Sai: mọi dòng mở cùng hồ sơ mẫu. Đúng: truyền ID đối tượng, kiểm tên ở chi tiết và kết quả.
Sai: Back làm mất ngày đã chọn. Đúng: giữ bản nháp và trở về đúng màn gọi.

Một luồng nhỏ gộp vào ghi chú hiện có; không bắt tạo nhiều tài liệu.
Dùng [task-flow](../templates/ux/task-flow.md) và [wireframe-spec](../templates/ux/wireframe-spec.md).

Mở [chi tiết](references/practice-detail.md) khi cần mô hình tác vụ, chọn navigation, inventory lớn hoặc UX Readiness;
[thực hành](references/ux-structure-practice.md) khi cần ký pháp và tradeoff. Không đọc cả references mặc định.
