---
name: ui-craft-and-visual-qa
description: Soát và sửa UI qua render: hierarchy, spacing, chữ, trạng thái, responsive và accessibility; tách kiểm luồng khỏi soát ảnh.
---

# Craft và kiểm tra thị giác

Theo [WORKFLOWS.md](../../WORKFLOWS.md). Dùng [FLOW.md](../../FLOW.md) cho hành vi.
Build/source không chứng minh giao diện đạt. Muốn kết luận phải mở ảnh render thật.

1. So tác vụ và luồng trước, rồi hierarchy, nội dung, tương tác, chữ, spacing, màu, ảnh.
2. Chạy [checker](scripts/README.md): static kiểm source/accessibility cơ bản; taste đo render;
   flow kiểm cấu trúc hành vi và ghi runtime `UNKNOWN` tới khi bấm thử có bằng chứng.
3. Chụp mobile/desktop, sáng/tối; kiểm console, tài nguyên lỗi, 320px reflow và trạng thái liên quan.
4. Mở ảnh và ghi vị trí, mức độ, cách sửa. Không suy từ số cảnh báo thành chất lượng tổng thể.
5. Sửa tại token/component/renderer nguồn, kiểm mọi route dùng chung khi đổi màu/button/navigation.
6. Chạy lại khu vực đổi; bàn giao lỗi còn mở và phần chưa kiểm (native, AT, backend, người dùng).

Hard blocker: chữ/CTA biến mất, tương phản gần 1:1, mất nội dung quan trọng, crop mất chủ thể,
flow chết hoặc quyền sai. Heuristic khoảng trống không buộc kéo card hay bịa dữ liệu lấp khung.
Sai: có screenshot là gọi đạt. Đúng: mở ảnh, ghi quan sát và kiểm hành vi riêng.

## Cải thiện giao diện hiện có

Giữ brand, flow và convention nếu không được yêu cầu redesign; sửa đúng owner.
Mở [chi tiết](references/practice-detail.md#cải-thiện-giao-diện-hiện-có) khi cần vòng polish đầy đủ.

## Soát prototype

Phân biệt gallery/artboard và prototype bấm được. Thử tác vụ chính, Back, sửa, nhánh lỗi và dữ liệu.
Mở [chi tiết](references/practice-detail.md#soát-prototype) khi có nhiều màn/trạng thái.

Chỉ mở [craft standards](references/craft-standards.md) khi token/CRAFT chưa đủ cho quyết định;
[web app patterns](references/web-app-patterns.md) khi có dashboard/bảng/form dày;
[sanity gate](checklists/elementary-visual-sanity-gate.md) khi sửa theme/shared surface/crop;
[chi tiết review](references/practice-detail.md) khi cần đủ bảy dấu hiệu, media resolution,
text-on-image, surface-pair hoặc regression xuyên trang. Mỗi dấu hiệu ghi `not present / clearly purposeful / needs repair`.
