# Tài khoản và khôi phục

Hướng dẫn con của [`interaction-patterns-and-form-ux`](../../SKILL.md); trước đây là skill riêng `authentication-account-and-recovery-ux`.

Chọn cỡ/track theo [WORKFLOWS.md](../../../../WORKFLOWS.md), không tự mở thêm quy trình.

Kiểm đăng nhập/đăng ký, phiên, quên mật khẩu, xác thực và trở lại tác vụ. Giữ input an toàn, lỗi cụ thể tránh lộ tài khoản; phân biệt quyền và trạng thái xác thực.

Sai: lỗi đăng nhập xoá form. Đúng: giữ trường phù hợp và có đường thử lại.

Ghi quyết định, bằng chứng và giới hạn trong ghi chú hiện có; dùng PASS / FAIL / UNKNOWN.
Từ cỡ M, áp dụng [FLOW.md](../../../../FLOW.md) cho đối tượng, vai trò, Back, dữ liệu và hậu quả.

Khi có ngoại lệ, nhiều trạng thái, cần đặc tả đầy đủ hoặc handoff chuyên môn,
mở [thực hành chuyên sâu](practice-detail.md); file này giữ toàn bộ hướng dẫn trước khi rút gọn.
Tra đúng mẫu khi cần: [references theo tác vụ](auth-decision-reference.md).
