# Review độc lập — 05-native-gate

Reviewer: fresh-gate-review-2026-10-30 · agent-heuristic · independent: true · first-review.

Các tác vụ đọc bài, xin nghỉ, lỗi ngày và hủy đơn hiểu được; iOS sheet và Android toàn màn đã khác nhau. Tuy nhiên copy gửi/lưu chưa thống nhất, nhịp cuối form cần xác minh, cá tính giáo dục và mức khác biệt nền tảng còn ở mức khá cơ bản. Không ghi hard fail chắc chắn từ tập ảnh.

Điểm trung bình: **3.75/5**. Điểm 10 chiều: 1: 4 · 2: 4 · 3: 3.5 · 4: 4 · 5: 4 · 6: 4 · 7: 3.5 · 8: 3.5 · 9: 3.5 · 10: 3.5.

Hard fail chắc chắn quan sát được: **0**. Điều này không xác nhận mọi hard-fail check đều PASS; các kiểm tra ngoài ảnh nằm trong not_checked.

Điểm heuristic chưa đạt ngưỡng L về trung bình 4.0; các nhận xét cần sửa có trong review.json.

## Tính độc lập và giới hạn

Chỉ đọc brief, manifest, REVIEWER, rubric, review.template và mở toàn bộ 14 ảnh trong chính packet. Không đọc source, rationale hoặc điểm tác giả.

Sai lệch thủ tục: brief đã được đọc trước ảnh do lần đọc gộp đầu. Mục cold ghi ấn tượng đầu sau brief, **không phải cold review đúng thứ tự**; không thể dùng phần này như bằng chứng đọc lạnh hợp lệ. Cần reviewer khác chưa đọc brief nếu muốn đạt điều kiện đó.

Không coi nội dung bên dưới viewport là bị mất. Không suy ra kích thước hit target, tỷ lệ contrast, keyboard path, AT, native behavior hoặc lỗi runtime từ ảnh tĩnh.

## Ghi nhận cụ thể

- Chiều 3 · 05-Android-request-light.png · CTA Gửi đơn xin nghỉ sát mép đáy và home indicator: Kiểm tra insets cuối vùng cuộn và thêm khoảng trống đủ để CTA nằm trọn bên trên home indicator khi cuộn cuối; không coi ảnh này là bằng chứng CTA không thể tiếp cận.
- Chiều 7 · 05-iOS-date-error.png · Thông báo Ngày nghỉ đã qua trong khi ô ngày ở ngoài vùng thấy: Đưa focus/scroll về ô ngày lỗi hoặc có hành động Chọn lại ngày; xác minh cả bàn phím và VoiceOver ở runtime.
- Chiều 8 · 05-Android-request-light.png · Gửi đơn xin nghỉ và chú thích Chỉ lưu đơn minh hoạ trên máy này, chưa gửi cho cô: Đổi CTA thành Lưu đơn minh hoạ hoặc mô phỏng hành động gửi với nhãn minh hoạ nhất quán; tránh hai nghĩa khác nhau trong cùng một thao tác.
- Chiều 9 · 05-native-1280-light.jpg · Danh sách bài và lịch của hai nền tảng có cấu trúc gần như nhau: Tinh chỉnh tỷ lệ tiêu đề, nhóm list và khoảng cách theo iOS/Material 3; kiểm native controls, back và text scaling trên thiết bị trước khi gọi native-ready.
- Chiều 10 · 05-native-390-light.jpg · Bề mặt tím xám, danh sách hộp và avatar ký tự: Tạo chi tiết nhận diện giáo dục có mục đích, chẳng hạn cấu trúc thông báo cô và thông tin học sinh rõ hơn; giữ hệ token nhất quán và tránh thêm trang trí ngẫu nhiên.

## Chưa kiểm

- Bàn phím, thứ tự Tab và focus qua toàn bộ luồng; ảnh focus riêng lẻ không chứng minh toàn luồng.
- VoiceOver, TalkBack, tên và vai trò accessible, thứ tự đọc.
- Phóng chữ 200%, Dynamic Type và cỡ chữ hệ thống lớn.
- Vùng hit target thực tế; kích thước hình vẽ không xác nhận vùng chạm.
- Đo contrast AA bằng pixel/token đầy đủ, gồm mọi trạng thái.
- Điều hướng back, cuộn tới cuối, click, loading, lưu và khôi phục dữ liệu ở runtime.
- Tính đầy đủ của các màn/trạng thái/theme không có ảnh trong packet; không suy ra là source thiếu.
- Cold review đúng thứ tự: brief đã được đọc trước ảnh; cold bên dưới là ấn tượng đầu sau brief và không phải đọc lạnh hợp lệ.
- Native runtime, safe area, edge swipe, Android back và rendering bằng framework native chưa được kiểm chứng; packet tự ghi browser preview.
- Mọi màn ở cả hai theme chưa có đủ ảnh trạng thái tương ứng.
