# Gu thiết kế

Nguyên tắc chủ repo đã yêu cầu ở các dự án trước. Áp dụng từ bản đầu tiên. Dự án cụ thể yêu cầu khác
thì làm theo dự án và ghi lý do. File do chủ repo sở hữu; mỗi dòng ngắn, nhìn ảnh là kiểm được.

**File này đứng trên `FLOW.md`, `CRAFT.md`, skill, rubric và checker.** Các tài liệu đó chỉ được làm chặt
hơn hoặc nói cách làm; không được nới một dòng ở đây thành "gợi ý" hay thêm ngoại lệ. Muốn đổi thì sửa
file này, do chủ repo duyệt.

## Phong cách chung

- Minimalism, hiện đại, **khoảng thở có chủ đích**: bớt nhiễu (màu, viền, bóng, chữ thừa), không bớt thông
  tin. Màn gọn mà vẫn đầy đặn.
- Không rối màu. Màu nhấn chỉ cho thứ thật sự quan trọng.
- Mỗi màn **một** thông tin chính; phân cấp chính, phụ nhìn ra ngay. Thừa thì tách màn hoặc thu gọn.
- Không để màn trống: không mảng trống lớn ở đáy, bên phải hay giữa các khối. Thiếu nội dung thì thu khung,
  chia lại cột hoặc thêm thông tin có ích; không kéo giãn khoảng cách hay card để lấp. Đổi nội dung xong thì
  đo lại chiều cao khung.

## Bố cục desktop

- Từ 1024 px dùng lưới 12 cột. Không để một cột hẹp lọt thỏm giữa khung rộng: form dài đi kèm cột phụ,
  danh sách đi kèm vùng chi tiết.
- Mật độ theo loại màn trong [`layout-and-density.md`](foundations/layout-and-density.md).

## Card

- Bo góc **đồng nhất** trên toàn sản phẩm, độ bo theo brand brief, không mặc định 24px.
- Font, cỡ chữ, bố cục chọn theo chức năng từng màn, không rập một khuôn.
- Card nổi bật (nền thương hiệu đậm, chữ trắng): tối đa một mỗi màn, màu từ brand brief (không mặc định
  navy), tối thiểu 3 tầng: nhãn, thông tin chính, ngữ cảnh (so sánh, tiến độ, hạn, bước tiếp). Nút trên
  card nền đậm là nút trắng.
- Hoạ tiết trang trí không bao giờ đè lên chữ.
- Card thường có tiêu đề, nội dung, chỗ cho hành động hoặc trạng thái; nội dung phủ phần lớn card.
- **Không thanh màu bên trái card** hay dòng. Trạng thái dùng nhãn chữ, chip hoặc icon.
- Card chứa danh sách dòng không có padding thừa: dòng đầu, dòng cuối sát padding thường của card.
- Cùng loại card trông giống hệt nhau trên mọi màn (ví dụ dòng nào cũng có chevron ">"), bất kể giới hạn
  của prototype.
- Trước khi tự chế card, xem [`design-system/patterns/`](design-system/patterns/README.md).

## Kích thước và điều hướng app

- Vùng chạm ≥ 44 px. Chữ phụ ≥ 12 px.
- Bottom nav: tab đang chọn nở thành viên (pill) icon trái, nhãn phải; tab khác chỉ icon. Viên không chạm mép nav.
- Nội dung và nút không bị thanh cố định (bottom nav, thanh hành động) che.
- Màn con mở từ trang chủ có Back trên appbar, không tô sáng một tab.

## Luồng và hành động

- Mọi nút, dòng bấm được dẫn tới màn thật; không `href="#"` cho hành động chính. Màn mới có ít nhất một đường vào.
- Back về đúng màn vừa rời. Người dùng luôn ở trong role của mình (đăng nhập, đăng xuất, quên mật khẩu, nav).
- Trường trong form không nhảy sang luồng khác; picker/sheet riêng và quay về đúng form.
- Không mở nhầm đối tượng: mỗi dòng, chat, môn, buổi, file mở đúng chính nó. Thiếu màn thì dựng màn mẫu đúng nghĩa.
- Việc không hoàn tác hoặc liên quan tiền (rời, xoá, chặn, giải tán, khoá tài khoản, đăng xuất, rút tiền,
  thu phí, nhắc hàng loạt) **luôn** có sheet xác nhận có Hủy, rồi màn kết quả. Tin hàng loạt dùng biến
  theo từng người.
- Hành động chính (Lưu, Gửi, Tạo, Duyệt) có màn kết quả hoặc thẻ trạng thái; màn quay về hiện số đã cập nhật.
  Hoàn tác về đúng trạng thái trước.
- Nút chính khoá khi thiếu dữ liệu, kèm lý do. Hành động theo thời gian hiện đúng trạng thái (chưa mở, đã khoá).

## Chữ trên màn

- Ngắn gọn; không câu mô tả khi giao diện tự nói lên.
- **Không dòng giải thích phụ** dưới tiêu đề, trên card hay màn (ghi chú kỳ, thời điểm cập nhật, "bấm để…",
  cách hệ thống hoạt động, chú giải biểu đồ, "đã thông báo X"). Chỉ giữ lý do lỗi, dữ liệu thật, trạng thái.
- **Không ghi chú bản mẫu trên màn** ("dữ liệu mẫu", "minh hoạ", "bản mẫu…", công tắc vai trò để demo);
  ghi trong phần bàn giao. Không lộ `{{biến}}` hay ghi chú nội bộ.
- **Không nối cụm từ bằng " · "**; viết lại bằng khoảng trắng, xuống dòng có chủ đích, từ nối hoặc câu.
- Một khái niệm một thuật ngữ. Nhãn nút tối đa 3 từ, động từ + đối tượng, cùng nhãn trên nút, tiêu đề sheet
  xác nhận và nút xác nhận; tên quen thuộc ("Hủy", không "Rút đề xuất"). Ngày luôn kèm thứ hoặc ngày tháng.
- Không xuống dòng vô cớ; không thu nhỏ chữ để che lỗi layout.

## Khi soát bản mẫu

Dữ liệu mẫu chỉ là chỗ giữ chỗ: không tốn công sửa lệch tên, số, ngày giữa các màn; tập trung lỗi giao diện và luồng.

## Trước khi giao

```sh
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs <trang.html> --screenshot qa/
```

Mặc định 390 px và 1280 px, sáng và tối; desktop và artboard thêm `--layout strict`. Không chạy được thì
chạy `static-check.cjs` và soát bằng mắt theo [README công cụ QA](skills_UIUX/ui-craft-and-visual-qa/scripts/README.md).

- [ ] Script không còn lỗi; từng cảnh báo đã sửa hoặc có lý do giữ.
- [ ] Đã mở ảnh từng màn ở điện thoại và máy tính, sáng và tối, và đối chiếu từng mục ở trên.
- [ ] Màu, font, bo góc từ brand brief, không phải mặc định của starter; che tên vẫn nhận ra ngành.

## Vòng học của gu

Lỗi mà `taste-check` và rubric bỏ qua: ghi một dòng vào [`TASTE-LOG.md`](TASTE-LOG.md). Lặp từ hai dự án,
hoặc chủ repo yêu cầu trực tiếp, thì đưa lên file này. Đo được bằng DOM thì thêm vào `taste-check.cjs` kèm
test. Quy tắc hết đúng thì chỉ chủ repo xoá, ghi lý do vào log.
