---
name: frontend-implementation
description: Dựng giao diện. Dùng theo tác vụ được chọn trong WORKFLOWS.md.
---

# Dựng giao diện

Chọn cỡ/track theo [WORKFLOWS.md](../../WORKFLOWS.md), không tự mở thêm quy trình.

Đọc flow/component/token hiện có, sửa đúng source và convention. Dùng HTML semantic, responsive theo nội dung, state đầy đủ, tránh JS client dư. Kiểm build/lint/test liên quan, render và hành vi.

Sai: thêm CSS đè cuối để sửa toàn app. Đúng: sửa component chủ và kiểm regression.

Ghi quyết định, bằng chứng và giới hạn trong ghi chú hiện có; dùng PASS / FAIL / UNKNOWN.
Từ cỡ M, áp dụng [FLOW.md](../../FLOW.md) cho đối tượng, vai trò, Back, dữ liệu và hậu quả.

Khi có ngoại lệ, nhiều trạng thái, cần đặc tả đầy đủ hoặc handoff chuyên môn,
mở [thực hành chuyên sâu](references/practice-detail.md); file này giữ toàn bộ hướng dẫn trước khi rút gọn.
Tra đúng mẫu khi cần: [references theo tác vụ](references/implementation-patterns.md), [checklists theo tác vụ](checklists/frontend-gate.md), [examples theo tác vụ](examples/page-composition.md).
