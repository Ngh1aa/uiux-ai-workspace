---
name: data-tables-and-enterprise-ux
description: Bảng dữ liệu cho tác vụ. Dùng theo tác vụ được chọn trong WORKFLOWS.md.
---

# Bảng dữ liệu cho tác vụ

Chọn cỡ/track theo [WORKFLOWS.md](../../WORKFLOWS.md), không tự mở thêm quy trình.

Cột theo quyết định; định danh rõ, trạng thái có chữ, số căn phải/đơn vị/tabular-nums. Xác định sort/filter/selection/pagination và giữ ngữ cảnh Back. Dùng table semantic; grid chỉ khi có keyboard model tương ứng. Kiểm loading/empty/error/permission, bulk hậu quả và responsive.

Sai: ẩn cột quyết định trên mobile. Đúng: giữ định danh/đơn vị/hành động, chọn list hay scroll theo tác vụ.

Ghi quyết định, bằng chứng và giới hạn trong ghi chú hiện có; dùng PASS / FAIL / UNKNOWN.
Từ cỡ M, áp dụng [FLOW.md](../../FLOW.md) cho đối tượng, vai trò, Back, dữ liệu và hậu quả.

Khi có ngoại lệ, nhiều trạng thái, cần đặc tả đầy đủ hoặc handoff chuyên môn,
mở [thực hành chuyên sâu](references/practice-detail.md); file này giữ toàn bộ hướng dẫn trước khi rút gọn.
Tra đúng mẫu khi cần: [references theo tác vụ](references/table-patterns.md), [checklists theo tác vụ](checklists/table-gate.md).
