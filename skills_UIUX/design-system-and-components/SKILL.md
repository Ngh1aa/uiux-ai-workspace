---
name: design-system-and-components
description: Hệ thống thiết kế. Dùng theo tác vụ được chọn trong WORKFLOWS.md.
---

# Hệ thống thiết kế

Chọn cỡ/track theo [WORKFLOWS.md](../../WORKFLOWS.md), không tự mở thêm quy trình.

Tìm token/component đang có trước khi thêm. Tách primitive/semantic/component, trạng thái và accessibility; giữ parity sáng/tối, export và hợp đồng. Test biến thể và nơi dùng chung.

Sai: thêm màu hex ở từng màn. Đúng: sửa semantic role và kiểm toàn bộ consumer.

Ghi quyết định, bằng chứng và giới hạn trong ghi chú hiện có; dùng PASS / FAIL / UNKNOWN.
Từ cỡ M, áp dụng [FLOW.md](../../FLOW.md) cho đối tượng, vai trò, Back, dữ liệu và hậu quả.

Khi có ngoại lệ, nhiều trạng thái, cần đặc tả đầy đủ hoặc handoff chuyên môn,
mở [thực hành chuyên sâu](references/practice-detail.md); file này giữ toàn bộ hướng dẫn trước khi rút gọn.
Tra đúng mẫu khi cần: [references theo tác vụ](references/component-contracts.md), [checklists theo tác vụ](checklists/component-gate.md), [examples theo tác vụ](examples/component-spec.md).
