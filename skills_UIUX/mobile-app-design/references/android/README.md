# Thiết kế Android

Hướng dẫn con của [`mobile-app-design`](../../SKILL.md); trước đây là skill riêng `android-app-design`.

Chọn cỡ/track theo [WORKFLOWS.md](../../../../WORKFLOWS.md), không tự mở thêm quy trình.

Xác định SDK/toolkit hiện có; chọn navigation và Back/Up trước chrome. Kiểm insets, IME, 48dp, chữ sp, TalkBack, khôi phục state; không đổi framework để giống Material.

Sai: co màn điện thoại cho tablet. Đúng: đổi panes theo không gian và giữ back stack.

Ghi quyết định, bằng chứng và giới hạn trong ghi chú hiện có; dùng PASS / FAIL / UNKNOWN.
Từ cỡ M, áp dụng [FLOW.md](../../../../FLOW.md) cho đối tượng, vai trò, Back, dữ liệu và hậu quả.

Khi có ngoại lệ, nhiều trạng thái, cần đặc tả đầy đủ hoặc handoff chuyên môn,
mở [thực hành chuyên sâu](practice-detail.md); file này giữ toàn bộ hướng dẫn trước khi rút gọn.
Tra đúng mẫu khi cần: [references theo tác vụ](android-spec-sheet.md).
