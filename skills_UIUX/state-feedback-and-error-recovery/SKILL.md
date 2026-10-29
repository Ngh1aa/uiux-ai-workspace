---
name: state-feedback-and-error-recovery
description: Trạng thái và khôi phục. Dùng theo tác vụ được chọn trong WORKFLOWS.md.
---

# Trạng thái và khôi phục

Chọn cỡ/track theo [WORKFLOWS.md](../../WORKFLOWS.md), không tự mở thêm quy trình.

Liệt kê default/loading/empty/error/stale/success/offline/permission phù hợp. Mỗi trạng thái nói điều xảy ra và bước tiếp theo; giữ dữ liệu, chống gửi lặp và retry không nhân đôi hậu quả.

Sai: spinner vô hạn. Đúng: thông báo lỗi cụ thể, giữ form và thử lại.

Ghi quyết định, bằng chứng và giới hạn trong ghi chú hiện có; dùng PASS / FAIL / UNKNOWN.
Từ cỡ M, áp dụng [FLOW.md](../../FLOW.md) cho đối tượng, vai trò, Back, dữ liệu và hậu quả.

Khi có ngoại lệ, nhiều trạng thái, cần đặc tả đầy đủ hoặc handoff chuyên môn,
mở [thực hành chuyên sâu](references/practice-detail.md); file này giữ toàn bộ hướng dẫn trước khi rút gọn.
