# Review độc lập — 04-multi-role-gate

Reviewer: fresh-gate-review-2026-10-30 · agent-heuristic · independent: true · first-review.

Lịch theo ghế, cảnh báo trễ và phân vùng chi tiết có trật tự; màn bác sĩ đưa dị ứng lên rõ, màn doanh thu ghi trung thực phần dữ liệu thiếu. Các vai trò dùng chung khung nhất quán. Không ghi hard fail chắc chắn từ tập ảnh.

Điểm trung bình: **4.15/5**. Điểm 10 chiều: 1: 4.5 · 2: 4.5 · 3: 4 · 4: 4 · 5: 4 · 6: 4.5 · 7: 4 · 8: 4 · 9: 4 · 10: 4.

Hard fail chắc chắn quan sát được: **0**. Điều này không xác nhận mọi hard-fail check đều PASS; các kiểm tra ngoài ảnh nằm trong not_checked.

Điểm heuristic đạt ngưỡng L trên phạm vi ảnh; chưa đủ để chứng nhận runtime, accessibility hay nghiệm thu sản phẩm.

## Tính độc lập và giới hạn

Chỉ đọc brief, manifest, REVIEWER, rubric, review.template và mở toàn bộ 10 ảnh trong chính packet. Không đọc source, rationale hoặc điểm tác giả.

Sai lệch thủ tục: brief đã được đọc trước ảnh do lần đọc gộp đầu. Mục cold ghi ấn tượng đầu sau brief, **không phải cold review đúng thứ tự**; không thể dùng phần này như bằng chứng đọc lạnh hợp lệ. Cần reviewer khác chưa đọc brief nếu muốn đạt điều kiện đó.

Không coi nội dung bên dưới viewport là bị mất. Không suy ra kích thước hit target, tỷ lệ contrast, keyboard path, AT, native behavior hoặc lỗi runtime từ ảnh tĩnh.

## Ghi nhận cụ thể

- Chiều 7 · 04-patient-light.png · Badge Chưa đến và CTA Bắt đầu khám: Làm rõ bước xác nhận người bệnh đã có mặt trước khi bắt đầu; kiểm guard runtime, không suy ra guard bị thiếu chỉ từ ảnh.
- Chiều 3 · 04-multi-role-1440-light.jpg · Lưới lịch với các hàng khoảng 100 px: Thử giảm nhẹ chiều cao hàng nhưng giữ đủ vùng click và ba dòng trạng thái để xem nhiều lịch hơn trong 900 px.
- Chiều 9 · 04-multi-role-390-light.jpg · Cụm thương hiệu, giờ mở cửa và bộ đổi vai trên cùng: Nếu mobile thuộc scope tiếp theo, gom metadata header để đưa lịch và người muộn lên sớm hơn.

## Chưa kiểm

- Bàn phím, thứ tự Tab và focus qua toàn bộ luồng; ảnh focus riêng lẻ không chứng minh toàn luồng.
- VoiceOver, TalkBack, tên và vai trò accessible, thứ tự đọc.
- Phóng chữ 200%, Dynamic Type và cỡ chữ hệ thống lớn.
- Vùng hit target thực tế; kích thước hình vẽ không xác nhận vùng chạm.
- Đo contrast AA bằng pixel/token đầy đủ, gồm mọi trạng thái.
- Điều hướng back, cuộn tới cuối, click, loading, lưu và khôi phục dữ liệu ở runtime.
- Tính đầy đủ của các màn/trạng thái/theme không có ảnh trong packet; không suy ra là source thiếu.
- Cold review đúng thứ tự: brief đã được đọc trước ảnh; cold bên dưới là ấn tượng đầu sau brief và không phải đọc lạnh hợp lệ.
