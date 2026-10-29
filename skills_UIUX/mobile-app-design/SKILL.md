---
name: mobile-app-design
description: Thiết kế app mobile. Dùng theo tác vụ được chọn trong WORKFLOWS.md.
---

# Thiết kế app mobile

Chọn cỡ/track theo [WORKFLOWS.md](../../WORKFLOWS.md), không tự mở thêm quy trình.

Chốt platform/OS, brand, tác vụ và state trước UI. Giữ nghĩa/dữ liệu chung, chrome riêng; navigation, Back, draft, permission và recovery có test. Browser prototype chỉ chứng minh browser, native/AT ghi UNKNOWN khi chưa chạy.

Sai: iOS và Android chỉ đổi icon. Đúng: sheet iOS và full-screen Android theo tác vụ, cùng dữ liệu.

Ghi quyết định, bằng chứng và giới hạn trong ghi chú hiện có; dùng PASS / FAIL / UNKNOWN.
Từ cỡ M, áp dụng [FLOW.md](../../FLOW.md) cho đối tượng, vai trò, Back, dữ liệu và hậu quả.

Khi có ngoại lệ, nhiều trạng thái, cần đặc tả đầy đủ hoặc handoff chuyên môn,
mở [thực hành chuyên sâu](references/practice-detail.md); file này giữ toàn bộ hướng dẫn trước khi rút gọn.
Tra đúng mẫu khi cần: [references theo tác vụ](references/mobile-design-system-and-handoff.md), [checklists theo tác vụ](checklists/design-handoff.md).
