# Gu thiết kế

Đây là các nguyên tắc chủ repo đã yêu cầu ở những dự án trước. Áp dụng từ bản đầu tiên.
Khi một yêu cầu của dự án cụ thể khác với file này, làm theo dự án và ghi lại lý do.

File này do chủ repo sở hữu: thêm, sửa hoặc xoá dòng nào tuỳ ý. Mỗi dòng nên ngắn và kiểm
tra được bằng mắt.

## Phong cách chung

- Minimalism, hiện đại, **khoảng thở có chủ đích**. Minimalism là bớt nhiễu (màu, viền, bóng, chữ thừa),
  không phải bớt thông tin hay để màn trống. Màn gọn mà vẫn đầy đặn.
- Không rối màu. Màu nhấn chỉ dùng cho thứ thật sự quan trọng, không highlight tràn lan.
- Mỗi màn có **một** thông tin chính rõ ràng; phân cấp chính, phụ phải nhìn ra ngay.
- Không nhồi quá nhiều thông tin trong một màn. Thừa thì tách màn hoặc thu gọn.
- Khoảng trống xét theo tác vụ và nội dung thật; form ngắn có thể kết thúc sớm. Thu khung/chia cột khi hữu ích,
  không kéo giãn card hoặc bịa thêm dữ liệu để lấp viewport.

## Bố cục desktop

- Màn từ 1024 px trở lên dùng lưới 12 cột. Không để một cột hẹp nằm lọt thỏm giữa khung rộng: form dài
  đi kèm cột phụ (tóm tắt, mốc thời gian, trợ giúp); danh sách đi kèm vùng xem chi tiết.
- Chọn mật độ theo loại màn trong
  [`layout-and-density.md`](foundations/layout-and-density.md): thoáng cho trang giới thiệu, vừa cho
  app, gọn cho bảng quản trị.
## Card và bố cục

- Card bo góc tròn, **đồng nhất** bán kính trên toàn bộ sản phẩm. Độ bo theo tính cách thương hiệu
  (ghi trong brand brief), không mặc định 24px.
- Font, cỡ chữ và bố cục chọn theo chức năng của từng màn, không rập một khuôn cho mọi màn.
- Card nổi bật (nền màu thương hiệu đậm, chữ trắng) dùng để làm điểm nhấn cho thông tin quan trọng nhất.
  Màu nền lấy từ brand brief của dự án, không mặc định navy.
  Tối đa một card như vậy mỗi màn; màn nào đã ổn thì giữ nguyên, không bắt buộc màn nào cũng có.
- Card nổi bật không được chỉ có một con số trên nền màu. Tối thiểu 3 tầng: nhãn, con số hoặc thông tin
  chính, và một tầng ngữ cảnh (so sánh với kỳ trước, tiến độ, hạn, bước tiếp theo).
- Card thường cũng cần cấu trúc bên trong: tiêu đề, nội dung, và chỗ cho hành động hoặc trạng thái. Nội
  dung phải phủ phần lớn card; card cao mà chữ chỉ nằm ở đầu là card trống.
- Trước khi tự chế card, xem [`design-system/patterns/`](design-system/patterns/README.md): 30 khối ghép
  sẵn kèm mật độ tối thiểu và cách dùng sai của từng khối.
## Chữ trên màn

- Ngắn gọn, xúc tích. Không viết câu mô tả nếu giao diện đã tự nói lên.
- **Không nối cụm từ bằng " · "** (kiểu "Text A · Text B · Text C"). Viết lại theo nghĩa:
  tách bằng khoảng trắng, xuống dòng có chủ đích, dùng từ nối, hoặc viết thành câu.
- Không xuống dòng vô cớ. Kiểm tra chiều rộng, wrap và bố cục trước; rút câu khi giữ nguyên nghĩa.
  Cho phép xuống dòng tự nhiên với nội dung dài và chữ phóng lớn; không thu nhỏ chữ để che lỗi layout.

## Trước khi giao

Chạy script soát, nó kiểm tự động phần lớn danh sách dưới đây trên trang đã render:

```sh
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs <trang.html> --screenshot qa/
```

Mặc định soát ở 390 px và 1280 px, sáng và tối. Màn desktop và artboard canvas thêm `--layout strict`
để các cảnh báo bố cục (khoảng trống, độ phủ, thang chữ, card mỏng) thành lỗi. Không chạy được thì theo mục "Khi không chạy
được taste-check" trong [`START-HERE.md`](START-HERE.md).

- [ ] Script không còn lỗi; từng cảnh báo đã xem và sửa hoặc có lý do giữ.
- [ ] Không còn dấu " · " nối cụm từ trong nội dung.
- [ ] Không còn chữ gãy dòng ngoài ý muốn, không còn dòng cuối chỉ có một chữ.
- [ ] Mỗi màn có tối đa một card nổi bật, và card đó có đủ 3 tầng thông tin.
- [ ] Không còn cảnh báo `void`, `coverage`, `thin-highlight` (hoặc đã đánh dấu `data-whitespace` kèm lý do).
- [ ] Bán kính bo góc thống nhất giữa các card.
- [ ] Đã mở ảnh chụp ra nhìn từng màn ở cỡ điện thoại và máy tính, cả sáng và tối nếu có.
- [ ] Màu, font, bo góc đến từ brand brief của khách, không phải giá trị mặc định của starter kit.
- [ ] Che tên sản phẩm vẫn nhận ra ngành (xem `design-system/starter/SIGNATURE.md`).

## Vòng học của gu

Gu trong file này đến từ lỗi có thật, không từ danh sách chung. Mỗi lần chủ repo, khách hoặc người duyệt
độc lập bắt được một lỗi mà `taste-check` và rubric đều bỏ qua:

1. Ghi một dòng vào [`TASTE-LOG.md`](TASTE-LOG.md): ngày, dự án, ảnh hoặc màn, điều thấy, quy tắc rút ra.
2. Lỗi lặp lại từ hai dự án trở lên thì đưa quy tắc lên file này, viết sao cho nhìn ảnh là kiểm được.
3. Quy tắc đo được bằng DOM (khoảng trống, độ phủ, số chữ, khoảng cách) thì mở việc thêm vào
   `taste-check.cjs`, kèm một test tái hiện lỗi. Khi checker đã bắt, ghi tên cảnh báo vào dòng log.
4. Quy tắc không còn đúng thì xoá ở đây và ghi lý do vào log, không để quy tắc chết nằm lại.
