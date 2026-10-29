# Nhật ký gu

Mỗi dòng là một lỗi có thật mà checker và rubric chưa bắt được lúc đó. Cách dùng file này nằm ở mục
"Vòng học của gu" trong [`TASTE.md`](TASTE.md). Ghi mới ở cuối bảng; không sửa dòng cũ, chỉ cập nhật cột
"Đã thành".

| Ngày | Dự án, màn | Điều thấy | Quy tắc rút ra | Đã thành |
|---|---|---|---|---|
| 2026-10 | Trang thi STEM, màn đăng ký trên desktop | Form một cột hẹp giữa khung 1440, hai bên trống | Từ 1024 px, form dài đi kèm cột phụ (tóm tắt, mốc, trợ giúp) | TASTE "Bố cục desktop"; cảnh báo `void` |
| 2026-10 | Trang thi STEM, card kết quả | Card cao, chữ chỉ ở nửa trên, nửa dưới trống | Nội dung phủ phần lớn card | TASTE "Card và bố cục"; cảnh báo `coverage` |
| 2026-10 | Trang thi STEM, card nổi bật | Nền thương hiệu đậm chỉ có một con số | Card nổi bật cần nhãn, số chính và một tầng ngữ cảnh | TASTE "Card và bố cục"; cảnh báo `thin-highlight` |
| 2026-10 | Nhiều màn | Cụm "A · B · C" thay cho câu | Không nối cụm từ bằng " · " | TASTE "Chữ trên màn"; kiểm trong `taste-check` |
| 2026-10 | Thư viện pattern, khối mẫu | `flat-scale` báo trên khối minh hoạ vốn không phải màn đầy đủ | Khối minh hoạ đánh dấu `data-part`; checker bỏ qua thang chữ và độ phủ cho khối đó | `taste-check` (`data-part`) |
| 2026-10 | Starter iOS, sheet | Hộp thoại alert bo góc khác card bị báo lệch bán kính | Hộp thoại hệ thống theo nền tảng, không tính vào bán kính card | `taste-check` bỏ qua `role="alertdialog"` |
| 2026-10 | Starter Android, lớp phủ tối | Lớp phủ sau hộp thoại quá nhạt ở chế độ tối, nền vẫn đọc được | Lớp phủ đủ đậm để nền lùi hẳn (khoảng 56% ở chế độ tối) | Chưa; kiểm bằng mắt |
| 2026-10 | Nova v6, mọi màn | Yêu cầu làm lại toàn bộ giao diện nhưng nhánh chỉ thêm `nova-v6.css` nạp sau cùng (699 `!important`) và JS vá DOM; 0 dòng CSS cũ bị sửa; mất chất pastel iOS; màn vẫn trống, nhiều chữ vì markup cũ giữ nguyên | Redesign sản phẩm có code phải thay tại nguồn và xoá code bị thay; ghi và giữ ADN sản phẩm | Skill `brownfield-redesign`; `overlay-check.py` |
| 2026-10-29 | Benchmark v2, app sân | Source có 31 liên kết `href="#"`; bấm CTA Đặt sân này không đổi nội dung/kết quả. Ảnh gallery và điểm tự chấm 4 chưa chứng minh prototype hoạt động | Tách render, hành vi, rubric và review; dữ liệu lịch sử thiếu flow ghi UNKNOWN | FLOW; flow-check; [audit](benchmarks/evidence/2026-10-29/history-audit.json); runner/report |
| 2026-10-29 | Benchmark v2, landing gốm | Đã mở ảnh: bảng kem–đất nung và ba card giống cấu trúc, minh hoạ cốc SVG. Đây là tín hiệu cần xét theo ngành gốm, không tự kết luận xấu vì màu | Mẫu sửa tiếp giữ bảng màu có lý do, chuyển lớp sang hàng so sánh, thử serif có tiếng Việt; đánh giá bằng ảnh | CRAFT tín hiệu; iterative-repair 01 |
| 2026-10-29 | Benchmark v2, kho len | Source/ảnh có vạch trái dòng, caption đơn vị/kỳ/cập nhật và nhãn minh hoạ. Caption này giúp hiểu dữ liệu; vạch cần tránh thành tín hiệu duy nhất | Giữ nguồn/đơn vị/kỳ/minh hoạ, dùng trạng thái có chữ, không cấm caption/vạch tuyệt đối | FLOW; iterative-repair 03 |
