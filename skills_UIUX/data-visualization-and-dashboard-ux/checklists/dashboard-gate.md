# Dashboard Gate

Ghi PASS / FAIL / UNKNOWN cho từng mục, kèm bằng chứng (ảnh, dòng spec, kết quả checker).
Chạy trước: `taste-check.cjs "<trang>" --width 390 --width 1024 --width 1440 --layout strict`.
Mục có mã luật trong ngoặc là checker bắt được; mục còn lại soát bằng mắt. Khi chấm rubric, áp
[trần điểm dashboard](../../design-critique-and-rationale/references/dashboard-caps.md).

## Thứ tự và nhiệm vụ

- [ ] Hàng đầu trả lời câu hỏi chính của màn.
- [ ] Việc cần xử lý (cảnh báo, quá hạn) đứng trước số liệu tham khảo, ở cả desktop và mobile.
- [ ] Mỗi panel trả lời một câu hỏi và có một hành động hoặc người chịu trách nhiệm.

## Số và kỳ

- [ ] Mỗi delta có dấu, cơ sở so sánh và kỳ ("+4,1% so với quý 3 năm trước"); với chỉ số mà tăng là
      xấu (chi tiêu, lỗi), màu không báo "tốt".
- [ ] Đơn vị và kỳ nằm trong tiêu đề hoặc chip, và khớp khoảng mà biểu đồ vẽ.
- [ ] Giờ cập nhật hiện một chỗ ở panel chính; dữ liệu quá hạn làm cập nhật thì thành chip trạng thái.

## Biểu đồ

- [ ] Trục giá trị của cột và vùng bắt đầu từ 0, hoặc ngoại lệ có ghi.
- [ ] Donut/pie tối đa 3 phần (`chart-donut`); một con số % dùng thanh ngang (`chart-gauge`).
- [ ] Cột có giá trị đọc được (`chart-values`); nhãn trực tiếp, không chú giải ô màu (`chart-legend`).
- [ ] Không mã hoá chỉ bằng màu; đã xem mô phỏng mù màu.
- [ ] Màu trạng thái không làm màu dữ liệu (`status-series`).
- [ ] Mỗi biểu đồ có tên nêu kết luận (`chart-name`); biểu đồ quan trọng có tóm tắt chữ và bảng hoặc
      danh sách giá trị.
- [ ] Giá trị chỉ có trong tooltip thì bàn phím và chạm cũng xem được.

## Bố cục

- [ ] Lưới panel cân ở 1024, 1280, 1440: không panel trống đáy (`panel-void`), không panel lẻ (`panel-orphan`).
- [ ] Mobile: tối đa 4 panel đầy đủ, còn lại thành dòng tóm tắt; không cuộn ngang.

## Trạng thái và dữ liệu biên

- [ ] Tải, rỗng, không có dữ liệu, một phần, lỗi, không có quyền được định nghĩa cho từng panel.
- [ ] Một panel lỗi không làm trống cả dashboard.
- [ ] Đã thử với 0, null, giá trị ngoại lai, nhãn dài, một nhóm áp đảo.
