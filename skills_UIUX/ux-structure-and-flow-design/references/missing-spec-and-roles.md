# Khi thiếu spec, và khi một sản phẩm có nhiều vai trò

Dùng khi được nhờ thiết kế một vai trò, một khu vực hay một luồng mà không có tài liệu yêu cầu riêng,
hoặc khi cùng một sản phẩm phục vụ nhiều vai trò (ví dụ giáo vụ, giáo viên, trưởng bộ môn).

## 1. Hỏi một câu trước khi làm

Việc cỡ M trở lên mà thiếu spec thì tốn công làm lại nếu đoán sai. Hỏi **một** câu, có lựa chọn:

- "Bạn có tài liệu yêu cầu cho <vai trò> không, hay mình suy ra từ <các spec đang có>?"

Nếu không ai trả lời được (làm việc không có người theo dõi), chọn suy ra, ghi rõ ở đầu kết quả và
làm tiếp.

## 2. Gom mọi chỗ spec đang có nhắc tới vai trò đó

Đọc spec của các vai trò khác và ghi lại mọi câu có nhắc tới vai trò cần làm. Mỗi câu là một nghĩa
vụ hoặc một quyền. Ví dụ, spec giáo viên viết "báo cáo cần được Trưởng bộ môn và Giáo vụ thông qua"
nghĩa là trưởng bộ môn có màn duyệt, có hạn và có "yêu cầu làm lại".

| Câu trong spec | Nguồn | Suy ra cho vai trò | Mức chắc |
|---|---|---|---|
| <trích> | <file, mục> | <màn hoặc hành động> | `EVIDENCED` nếu spec nói thẳng, `HYPOTHESIS` nếu suy luận |

Chỉ phần `EVIDENCED` được coi là yêu cầu. Phần `HYPOTHESIS` vẫn thiết kế, nhưng liệt kê lại cho
người duyệt chốt.

## 3. Lấp chỗ trống bằng việc thường gặp của vai trò

Sau khi gom hết, hỏi: người giữ vai trò này cần biết gì mỗi ngày, quyết định gì, giao cho ai? Thêm
màn cho những việc đó, đánh dấu `HYPOTHESIS`. Không thêm tính năng chỉ vì "có thì hay". Mỗi màn
thêm vào phải trả lời được một câu hỏi thật của vai trò.

## 4. Giữ dữ liệu khớp giữa các vai trò

Khi một sản phẩm có nhiều vai trò, cùng một sự việc phải hiện giống nhau ở mọi nơi:

- Chung một "hôm nay" và giờ trong dữ liệu mẫu.
- Cùng một người, lớp, mã học sinh, con số ở mọi vai trò. Ví dụ báo cáo đã được trưởng bộ môn duyệt
  lúc 09:20 thì màn giáo viên cũng ghi 09:20, và không còn nằm trong hàng chờ của trưởng bộ môn.
- Cùng một phiếu việc thì trạng thái khớp ở cả người giao lẫn người nhận.
- Cùng thuật ngữ cho cùng một thứ ("Yêu cầu làm lại", không lúc "trả lại" lúc "bổ sung").

Ghi bảng dữ liệu mẫu dùng chung (người, lớp, mã, giờ) ở một chỗ và dựng màn từ bảng đó, không gõ tay
lại ở từng màn.

## 5. Khi giao

- Ghi rõ vai trò được làm theo spec nào, phần nào là suy luận.
- Liệt kê các quyết định cần chủ dự án chốt (quyền hạn, quy tắc tính hạn, ai thấy dữ liệu gì).
- Kết luận UX Readiness tối đa là `READY_WITH_RISKS` khi phần lớn yêu cầu là `HYPOTHESIS`.
