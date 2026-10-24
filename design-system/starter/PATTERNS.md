# Mẫu theo loại màn

Mỗi loại màn trả lời một câu hỏi chính của người dùng. Xác định câu hỏi đó trước, rồi mới xếp
nội dung. Màn mẫu chạy được nằm trong [`mobile.html`](mobile.html), [`web.html`](web.html) và
[`landing.html`](landing.html) (khung section landing page).

Áp dụng cùng [`TASTE.md`](../../TASTE.md). Nếu một quy tắc ở đây mâu thuẫn với yêu cầu của dự án,
theo dự án.

## Quy tắc chung cho mọi màn

- Một màn tối đa **một** card nổi bật (`.app-hero`). Thanh tab và nút chính không tính.
- Mọi card cùng một bán kính (`--ds-card-radius`). Khối lồng bên trong dùng bán kính nhỏ hơn.
- Một nút chính (nền đậm) cho mỗi vùng. Hành động phụ dùng nút nhạt (`.app-tonal`) hoặc link.
- Màu nhấn chỉ cho thương hiệu và cho cảnh báo thật (quá hạn, lỗi). Không tô màu để trang trí.
- Nhãn ngắn không xuống dòng. Hết chỗ thì rút chữ, không thu nhỏ dưới 12px.

## 1. Trang chủ

Câu hỏi: *Hôm nay tôi cần làm gì trước?*

- Card nổi bật chứa **một** con số hành động được (việc cần xử lý), kèm tiến độ. Không đặt 4–5
  chỉ số ngang hàng.
- Ngay dưới là 3 thao tác nhanh hay dùng nhất. Từ 4 thao tác trở lên thì đưa vào màn khác.
- Danh sách việc xếp theo hạn: nhóm "Hạn hôm nay" trước, mỗi dòng có nút hành động ngay trên dòng.
- Màu cảnh báo chỉ dùng cho việc sắp quá hạn, luôn kèm icon và chữ.

## 2. Danh sách

Câu hỏi: *Tôi tìm nhanh một mục trong nhiều mục thế nào?*

- Tiêu đề lớn, ô tìm kiếm, rồi bộ lọc dạng segmented (tối đa 3–4 lựa chọn, nhãn ngắn).
- Nhóm theo thứ người dùng nghĩ tới (khối, ngày, trạng thái), có số lượng ở đầu nhóm.
- Mỗi dòng: avatar hoặc icon, tên (đậm), một dòng phụ, trạng thái ở cuối. Không quá 2 dòng chữ.
- Trạng thái thường dùng badge trung tính; chỉ trạng thái cần chú ý mới có màu.
- Kết quả tìm rỗng thì có màn rỗng riêng và nút xoá bộ lọc.

## 3. Chi tiết

Câu hỏi: *Đây là ai hoặc cái gì, và tôi làm gì tiếp?*

- Card nổi bật nhỏ ở đầu nhận diện đối tượng (tên, mã, một thông tin phụ).
- Thông tin gom vào một card, chia khu bằng đường kẻ nét đứt, mỗi khu có nhãn in hoa nhỏ.
- Dòng thông tin dạng nhãn bên trái, giá trị bên phải. Thông tin bị hạn chế quyền thì ghi rõ.
- Hành động chính cố định ở đáy (`.app-footer`), nhãn nói rõ việc sẽ xảy ra ("Tạo lớp").

## 4. Biểu mẫu

Câu hỏi: *Tôi điền gì, và điền đúng chưa?*

- Thứ tự trường theo thứ tự người dùng nghĩ. Trường tự điền được thì khoá và ghi rõ.
- Nhãn luôn nằm trên trường, không dùng chữ gợi ý thay cho nhãn.
- Lựa chọn trong lưới (lịch, giờ): ô đã chọn có dấu tích và chữ, ô không chọn được có hoạ tiết
  và lý do ("GV bận"), không chỉ đổi màu.
- Lỗi hiện ngay dưới trường, nói cách sửa ("Chọn ngày từ 19/10 trở đi"), không chỉ báo "Sai".
- Nút gửi cố định ở đáy, cùng tên với tiêu đề màn.

## 5. Rỗng

Câu hỏi: *Vì sao không có gì, và giờ làm gì?*

- Nói cái gì trống và vì sao (chưa có dữ liệu, bộ lọc, đã làm xong hết).
- Một câu ngắn, không đổ lỗi cho người dùng. Trống vì đã xong hết thì báo tích cực.
- Một hành động tiếp theo bằng nút nhạt.

## 6. Đang tải

- Khung xương (skeleton) đúng hình nội dung thật: avatar tròn, hai dòng chữ dài ngắn khác nhau.
- Giữ nguyên tiêu đề, ô tìm kiếm và thanh tab để màn không nhảy khi dữ liệu về.
- Chỉ hiện khung xương khi tải lâu hơn khoảng 300 ms.

## 7. Lỗi

- Banner lỗi ở đầu màn: dòng đậm nói chuyện gì xảy ra, dòng thường nói dữ liệu của người dùng
  có bị mất không.
- Giữ nguyên những gì người dùng đã nhập hoặc chọn.
- Nút "Thử lại" là hành động chính; nếu hệ thống tự thử lại thì ghi rõ dưới nút.

## 8. Chọn nhanh và thanh thanh toán

Câu hỏi: *Tôi chọn được ngay không, và hết bao nhiêu?*

- Lựa chọn hay dùng (khung giờ, buổi, gói) bấm được **ngay trong danh sách** (`.app-slot`), không
  bắt mở trang chi tiết mới chọn được.
- Lựa chọn đang chọn có nền đậm; thẻ chứa nó có viền (`.app-pick[aria-current]`). Chỉ một lựa chọn
  đang chọn trong cả nhóm.
- Lựa chọn không chọn được có hoạ tiết, gạch ngang và một dòng lý do ("CN 9:00 đã hết chỗ").
- Thanh dưới đáy (`.app-checkout`) **luôn** hiện lựa chọn hiện tại và tổng tiền, cập nhật ngay khi
  đổi. Chưa chọn gì thì ghi "Chưa chọn …", tổng 0 và khoá nút.
- Nhãn nút nói đúng việc ("Đăng ký học thử"), không ghi chung chung "Tiếp tục".

## Web: trạng thái từng khối

Mẫu chạy được: [`web-states.html`](web-states.html).

- Mỗi khối dữ liệu tự có trạng thái riêng. Một khối lỗi không làm trống cả trang.
- **Đang tải:** khung xương đúng hình dòng thật, giữ nguyên tiêu đề khối, ghi "Đang tải".
- **Dữ liệu cũ:** vẫn hiện số liệu, dải vàng ở đầu khối nói cũ bao lâu và nút "Tải lại", nhãn
  "Dữ liệu cũ" cạnh tiêu đề. Không lặng lẽ hiện số cũ.
- **Lỗi:** dòng đỏ nói khối nào không tải được, một câu nói các khối khác vẫn dùng được, nút
  "Thử lại".
- **Rỗng vì đã xong:** báo tích cực ("Không còn yêu cầu chờ duyệt"), không bắt làm gì.
- Giờ cập nhật chung của trang đặt ở góc trên.

## Web: trang quản trị

- Thanh bên trái cho điều hướng, trang chính rộng tối đa khoảng 1180px.
- Một card nổi bật cho con số quan trọng nhất; các số phụ nằm cùng card, không tách thành nhiều
  card màu.
- Bảng: tiêu đề cột in hoa nhỏ, số căn phải và dùng chữ số đều (`tabular-nums`). Dưới 900px
  ẩn cột phụ, không cuộn ngang.
- Tiêu đề khu nằm ngoài card và thẳng hàng giữa các cột.

## Landing page

Câu hỏi: *Cái này có đáng để tôi bấm nút không?*

- Thứ tự mặc định theo [`landing.html`](landing.html): hero, bằng chứng, vấn đề, lợi ích, cách
  hoạt động, bảng giá, lời khách, câu hỏi, lời mời cuối. Bỏ section không có nội dung thật.
- Hero một lời hứa, một nút chính; bố cục lệch, hình thật. Không hero căn giữa với ảnh trừu tượng.
- Lợi ích là các hàng xen kẽ có bằng chứng, không phải ba card icon giống nhau.
- Cùng một hành động chính xuất hiện ở header, hero và lời mời cuối, cùng một nhãn.
- Logo khách, lời trích, con số chỉ dùng khi có thật và được phép; mẫu thì ghi "minh hoạ".

