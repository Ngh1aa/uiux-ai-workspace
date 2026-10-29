# Luồng và điều hướng

Chuẩn hành vi cho công việc từ cỡ M; thứ tự đọc do [WORKFLOWS.md](WORKFLOWS.md) quyết định.
Soát ảnh và kiểm luồng là hai bằng chứng riêng. Dữ liệu minh hoạ vẫn phải nhất quán xuyên luồng.

## Hành động, đối tượng và đường vào

- CTA thực hiện đúng việc, mở đúng đối tượng và giữ vai trò. Không giao liên kết giữ chỗ như hành động đã hoạt động.
- Form submit, chọn giờ, tăng số lượng, mở sheet, Back và delegated handler có thể xử lý tại chỗ; không bắt có `data-to` hay `onclick`.
- Prototype phải bấm được các tác vụ trong brief. Gallery/artboard chỉ minh hoạ phải ghi rõ phạm vi; không lấy ảnh gallery làm bằng chứng prototype hoạt động.
- Mỗi màn cần giải thích được đường vào. Màn khởi đầu, deep link, xác thực và trạng thái hệ thống có thể không có đường vào nội bộ.
- Back trở về ngữ cảnh vừa rời, giữ lựa chọn và bản nháp phù hợp; không làm rơi sang vai trò khác. Điều hướng theo tác vụ và nền tảng, không ép mọi app dùng một tab bar.

## Hậu quả, xác nhận và kết quả

- Chọn mức kiểm tra theo hậu quả, khả năng khôi phục, độ bất ngờ và phạm vi ảnh hưởng. Tiền, dữ liệu khó phục hồi, gửi hàng loạt cần xem đúng đối tượng, số tiền/phạm vi trước khi thực thi.
- Có thể dùng bước review, dialog/`alertdialog`, xác thực lại, hoặc undo đáng tin cậy theo rủi ro. Không bắt mọi hành động thêm hai màn.
- Kết quả có thể là màn riêng hoặc trạng thái ngay tại chỗ. Phải thấy việc đã xảy ra, dữ liệu sau hành động và bước tiếp theo.
- Lỗi có phản hồi cụ thể và đường khôi phục; giữ dữ liệu hợp lệ. Không báo thành công khi tác vụ thất bại.
- Nút khoá có lý do liên quan, đọc được và gắn với control; trạng thái loading tránh gửi lặp.

## Nội dung và tính nhất quán

- Chọn, tóm tắt, review và kết quả khớp đối tượng, vai trò, số lượng, tổng tiền, ngày giờ, trạng thái.
- Nhãn ngắn, rõ hành động; ba từ là gợi ý. Số, khung giờ và tên đối tượng được dùng khi giúp chọn đúng.
- Giờ hẹn cần ngày trong ngữ cảnh; status bar, giờ mở cửa lặp hằng ngày và trục biểu đồ không cần lặp ngày trên mọi nhãn.
- Giữ đơn vị, nguồn dữ liệu, thời điểm cập nhật, chú giải và nhãn minh hoạ khi giúp hiểu/ra quyết định. Chỉ bỏ lời hướng dẫn dư thừa.
- Cùng loại dòng có affordance tương ứng hành vi thật. Dòng khoá, tiêu đề nhóm và đối tượng có quyền khác nhau có thể khác.
- Giữ consistency theo component và vai trò; không cấm card, caption, vạch trạng thái hay một bảng màu chỉ vì hình thức.

## Kiểm trước khi giao

`flow-check.cjs` soát HTML tĩnh: lỗi chắc chắn, cảnh báo heuristic, phần runtime `UNKNOWN`.
Không dùng kết quả tĩnh để chứng minh toàn bộ đồ thị điều hướng, quyền backend hay nghiệp vụ đúng.
Hành động quan trọng phải có Playwright hoặc bằng chứng bấm thật tương đương:

1. Màn gốc → lựa chọn → kiểm tra phù hợp → kết quả.
2. Back về đúng ngữ cảnh, dữ liệu còn đúng.
3. Sửa lựa chọn, xác nhận lại, kiểm tổng và trạng thái.
4. Mở đúng đối tượng, đúng vai trò; thử đường không có quyền.
5. Một nhánh lỗi → khôi phục; thử rủi ro và chống gửi lặp nếu liên quan.

Ghi vào mẫu task-flow/bàn giao sẵn có, dùng `PASS / FAIL / UNKNOWN` từng điều:

```text
Luồng / đường vào:
Đối tượng / vai trò:
Back / giữ bản nháp:
Sửa → review → kết quả / dữ liệu và tổng tiền:
Lỗi → khôi phục / kiểm tra hậu quả:
Bằng chứng: lệnh, test, ảnh, hash source
Chưa kiểm: backend, native, thiết bị thật, người dùng thật
```
