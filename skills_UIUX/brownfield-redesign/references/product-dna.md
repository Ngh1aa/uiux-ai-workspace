# ADN của sản phẩm

Người dùng quen một sản phẩm nhận ra nó qua vài đặc điểm lặp lại. Redesign làm mất các đặc điểm đó thì
người dùng thấy như dùng app khác, và thương hiệu mất phần đã xây. Gu chung của repo (`TASTE.md`) dạy cách
làm đẹp, không biết sản phẩm này là ai; vì vậy ADN phải được ghi ra trước khi chọn hướng.

## 1. Cách tìm ADN

Nguồn, theo thứ tự tin cậy:

1. Tài liệu thiết kế của dự án: hợp đồng thị giác, design decisions, brand guide, README.
2. Logo, icon, ảnh màn hình đã công bố.
3. Code: tên file và token (`pastel-*`, `ios26-*`, `glass`), các lớp sửa lặp lại nhiều lần cho cùng một
   chất liệu (dấu hiệu chủ sản phẩm muốn giữ nó).
4. Lời người dùng hoặc chủ sản phẩm khi phàn nàn về bản mới ("mất chất pastel iOS").

Phép thử: che logo và tên, chỉ ra 5–8 thứ trên màn làm người quen nhận ra sản phẩm.

## 2. Bảng ADN

| Đặc điểm | Biểu hiện hiện tại | ADN hay lỗi thực thi | Hướng mới làm gì |
|---|---|---|---|
| Bảng màu | mint, sky, lavender từ logo | ADN | Giữ; cho mỗi màu một vai trò dữ liệu |
| Cách dùng màu | mỗi dòng giao dịch một nền pastel | Lỗi thực thi | Sửa: pastel chỉ cho nhóm có nghĩa |
| Chất liệu | nền mờ, lớp kính kiểu iOS | ADN | Giữ; giảm số lớp chồng |
| Font | font hệ thống Apple | ADN (theo hợp đồng) | Giữ; thêm font dự phòng cho máy khác |
| Bo góc | 8 bán kính khác nhau | Lỗi thực thi | Sửa: một thang bo |

Ví dụ trên lấy từ Nova. Mỗi dự án tự điền.

**ADN**: đặc điểm có chủ đích, gắn với nhận diện, người dùng nhận ra. **Lỗi thực thi**: cách thể hiện
sai của một đặc điểm (rối, thiếu tương phản, thiếu vai trò). Sửa lỗi thực thi không có nghĩa là bỏ đặc
điểm. Câu cần tự hỏi trước khi bỏ một đặc điểm: "Vấn đề là đặc điểm này, hay cách dùng nó?"

## 3. ADN và gu chung

- ADN thuộc tầng "yêu cầu riêng của dự án" trong thứ tự ưu tiên của [`AGENTS.md`](../../../AGENTS.md),
  đứng trên `TASTE.md`.
- `TASTE.md` nói "không rối màu" thì áp vào **cách dùng** pastel (ít nhóm, có vai trò), không áp vào việc
  có pastel hay không.
- `CRAFT.md` cấm một mặc định nào đó mà ADN dùng chính mặc định đó (ví dụ font hệ thống) thì giữ ADN và
  xử lý phần rủi ro (font dự phòng), ghi lý do.

## 4. ADN trong cổng duyệt hướng

- Ít nhất một hướng là **tiến hoá ADN**: giữ mọi đặc điểm ADN, sửa mọi lỗi thực thi, đổi bố cục và
  markup nếu cần.
- Mỗi hướng có dòng "ADN: giữ … / đổi … / bỏ …".
- Hướng bỏ ADN được phép nhưng phải nói thẳng với người quyết định ("hướng B bỏ pastel, Nova sẽ trông
  như một app ngân hàng trung tính"), và chỉ chọn khi họ chọn.

## 5. Kiểm ADN khi giao

- Che logo trên ảnh sau: các đặc điểm ADN còn nhìn thấy không?
- Đặt ảnh trước và sau cạnh nhau: khác biệt có thấy ngay ngoài màu và khoảng cách không?
- Gửi bảng ADN cho người duyệt độc lập, xin chấm thêm một dòng "giữ ADN: đạt / không đạt, vì sao".
