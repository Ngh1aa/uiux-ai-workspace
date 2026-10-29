---
name: ios-app-design
description: Thiết kế iOS. Dùng theo tác vụ được chọn trong WORKFLOWS.md.
---

# Thiết kế iOS

Chọn cỡ/track theo [WORKFLOWS.md](../../WORKFLOWS.md), không tự mở thêm quy trình.

Chọn theo deployment target, brand và control sẵn có. Phân biệt push/sheet/alert, dismissal và bản nháp; kiểm safe area, 44pt, Dynamic Type, VoiceOver, dark và Reduce Motion. Browser proof không thay native.

Sai: Back mất bản nháp. Đúng: giữ state khi đóng sheet và kiểm trên OS mục tiêu.

Ghi quyết định, bằng chứng và giới hạn trong ghi chú hiện có; dùng PASS / FAIL / UNKNOWN.
Từ cỡ M, áp dụng [FLOW.md](../../FLOW.md) cho đối tượng, vai trò, Back, dữ liệu và hậu quả.

Khi có ngoại lệ, nhiều trạng thái, cần đặc tả đầy đủ hoặc handoff chuyên môn,
mở [thực hành chuyên sâu](references/practice-detail.md); file này giữ toàn bộ hướng dẫn trước khi rút gọn.
Tra đúng mẫu khi cần: [references theo tác vụ](references/ios-spec-sheet.md).
