# Review độc lập — 02-app-gate

Reviewer: fresh-gate-review-2026-10-30 · agent-heuristic · independent: true · first-review.

Ảnh cho thấy luồng đặt sân rõ, thương hiệu xanh hợp hoạt động thể thao, lỗi tranh giờ có hướng khôi phục và lịch rỗng có CTA. Nhịp dọc trang chủ còn khiến liên kết tìm đủ sân sát tab bar. Không ghi hard fail chắc chắn từ tập ảnh.

Điểm trung bình: **4.05/5**. Điểm 10 chiều: 1: 4.5 · 2: 4 · 3: 3.5 · 4: 4 · 5: 4 · 6: 4 · 7: 4 · 8: 4.5 · 9: 4 · 10: 4.

Hard fail chắc chắn quan sát được: **0**. Điều này không xác nhận mọi hard-fail check đều PASS; các kiểm tra ngoài ảnh nằm trong not_checked.

Điểm heuristic đạt ngưỡng L trên phạm vi ảnh; chưa đủ để chứng nhận runtime, accessibility hay nghiệm thu sản phẩm.

## Tính độc lập và giới hạn

Chỉ đọc brief, manifest, REVIEWER, rubric, review.template và mở toàn bộ 9 ảnh trong chính packet. Không đọc source, rationale hoặc điểm tác giả.

Sai lệch thủ tục: brief đã được đọc trước ảnh do lần đọc gộp đầu. Mục cold ghi ấn tượng đầu sau brief, **không phải cold review đúng thứ tự**; không thể dùng phần này như bằng chứng đọc lạnh hợp lệ. Cần reviewer khác chưa đọc brief nếu muốn đạt điều kiện đó.

Không coi nội dung bên dưới viewport là bị mất. Không suy ra kích thước hit target, tỷ lệ contrast, keyboard path, AT, native behavior hoặc lỗi runtime từ ảnh tĩnh.

## Ghi nhận cụ thể

- Chiều 3 · 02-app-1280-light.jpg · Liên kết Xem cả 3 sân tối nay sát mép trên tab bar; thẻ lịch cao: Giảm chiều cao phần lịch sắp tới hoặc chỉnh nhịp cuối vùng nội dung để liên kết có khoảng thở khi xuất hiện; kiểm tra cuộn thực tế trước kết luận che khuất.
- Chiều 1 · 02-app-390-light.jpg · Lượt đặt sắp tới đứng trước việc tìm sân tối nay: Cân nhắc phiên bản thẻ lịch gọn hơn để tác vụ tìm giờ trống được nhìn thấy sớm hơn.
- Chiều 8 · 02-checkout-light.png · Dòng Tối nay, 18:00–19:00: Bổ sung ngày cụ thể cạnh Tối nay trên bước xác nhận để giảm nhầm khi xem lại thông tin.

## Chưa kiểm

- Bàn phím, thứ tự Tab và focus qua toàn bộ luồng; ảnh focus riêng lẻ không chứng minh toàn luồng.
- VoiceOver, TalkBack, tên và vai trò accessible, thứ tự đọc.
- Phóng chữ 200%, Dynamic Type và cỡ chữ hệ thống lớn.
- Vùng hit target thực tế; kích thước hình vẽ không xác nhận vùng chạm.
- Đo contrast AA bằng pixel/token đầy đủ, gồm mọi trạng thái.
- Điều hướng back, cuộn tới cuối, click, loading, lưu và khôi phục dữ liệu ở runtime.
- Tính đầy đủ của các màn/trạng thái/theme không có ảnh trong packet; không suy ra là source thiếu.
- Cold review đúng thứ tự: brief đã được đọc trước ảnh; cold bên dưới là ấn tượng đầu sau brief và không phải đọc lạnh hợp lệ.
