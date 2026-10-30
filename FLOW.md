# Luồng và điều hướng

Chuẩn hành vi cho công việc từ cỡ M; thứ tự đọc do [WORKFLOWS.md](WORKFLOWS.md) quyết định.
Soát ảnh và kiểm luồng là hai bằng chứng riêng.

File này nói **cách kiểm** luồng. Quy tắc về luồng, xác nhận, kết quả và câu chữ nằm ở
[TASTE.md](TASTE.md) mục "Luồng và hành động" và "Chữ trên màn"; TASTE thắng khi hai file khác nhau.
Không thêm ngoại lệ ở đây để nới một dòng của TASTE.

## Hành động, đối tượng và đường vào

- CTA thực hiện đúng việc, mở đúng đối tượng và giữ vai trò. Không giao liên kết giữ chỗ như hành động đã hoạt động.
- Form submit, chọn giờ, tăng số lượng, mở sheet, Back và delegated handler có thể xử lý tại chỗ; không bắt có `data-to` hay `onclick`.
- Prototype phải bấm được các tác vụ trong brief. Gallery/artboard chỉ minh hoạ phải ghi rõ phạm vi trong phần bàn giao; không lấy ảnh gallery làm bằng chứng prototype hoạt động.
- Mỗi màn cần giải thích được đường vào. Màn khởi đầu, deep link, xác thực và trạng thái hệ thống có thể không có đường vào nội bộ.
- Back trở về ngữ cảnh vừa rời, giữ lựa chọn và bản nháp phù hợp; không làm rơi sang vai trò khác. Điều hướng theo tác vụ và nền tảng.

## Hậu quả, xác nhận và kết quả

- Hành động không hoàn tác được hoặc liên quan tiền theo danh sách trong TASTE: sheet xác nhận có Hủy, hiện đúng đối tượng, số tiền hoặc phạm vi, rồi màn kết quả.
- Hành động chính khác (Lưu, Gửi, Tạo, Duyệt): màn kết quả hoặc thẻ trạng thái; màn quay về hiện số liệu đã cập nhật.
- Lỗi có phản hồi cụ thể và đường khôi phục; giữ dữ liệu hợp lệ. Không báo thành công khi tác vụ thất bại.
- Nút khoá có lý do liên quan, đọc được và gắn với control; trạng thái loading tránh gửi lặp.

## Nội dung và tính nhất quán

- Chọn, tóm tắt, xác nhận và kết quả khớp đối tượng, vai trò, số lượng, tổng tiền, ngày, trạng thái **trong một lượt thao tác**. Lệch tên hay số giữa các màn mẫu không liên quan đến lượt thao tác đó thì bỏ qua (xem TASTE "Khi soát bản mẫu").
- Câu chữ theo TASTE: nhãn nút tối đa 3 từ, ngày kèm thứ hoặc ngày tháng, không dòng giải thích phụ, không ghi chú bản mẫu trên màn.
- Cùng loại dòng hoặc card có affordance giống nhau. Dòng khoá và tiêu đề nhóm khác loại nên có thể khác.

## Kiểm trước khi giao

`flow-check.cjs` soát HTML tĩnh: lỗi chắc chắn, cảnh báo heuristic, phần runtime `UNKNOWN`.
Không dùng kết quả tĩnh để chứng minh toàn bộ đồ thị điều hướng, quyền backend hay nghiệp vụ đúng.
Hành động quan trọng phải có Playwright hoặc bằng chứng bấm thật tương đương:

1. Màn gốc → lựa chọn → xác nhận → kết quả.
2. Back về đúng ngữ cảnh, dữ liệu còn đúng.
3. Sửa lựa chọn, xác nhận lại, kiểm tổng và trạng thái.
4. Mở đúng đối tượng, đúng vai trò; thử đường không có quyền.
5. Một nhánh lỗi → khôi phục; thử rủi ro và chống gửi lặp nếu liên quan.

Ghi vào mẫu task-flow/bàn giao sẵn có, dùng `PASS / FAIL / UNKNOWN` từng điều:

```text
Luồng / đường vào:
Đối tượng / vai trò:
Back / giữ bản nháp:
Sửa → xác nhận → kết quả / dữ liệu và tổng tiền:
Lỗi → khôi phục / kiểm tra hậu quả:
Bằng chứng: lệnh, test, ảnh, hash source
Phần mô phỏng / dữ liệu mẫu:
Chưa kiểm: backend, native, thiết bị thật, người dùng thật
```
