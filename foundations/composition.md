# Bố cục và nhịp

Trang này trả lời: **làm sao một màn trông có chủ ý, không giống các khối xếp lần lượt từ trên xuống?**
[`layout-and-density.md`](layout-and-density.md) lo phần đo đạc (lưới, mật độ, khoảng trống); trang này lo
phần cảm nhận: cân bằng, nhịp, tương phản và sự khác biệt giữa các section.

## 1. Năm công cụ bố cục

| Công cụ | Ý nghĩa | Cách làm cụ thể |
|---|---|---|
| **Điểm nhìn** | Một thứ thắng mọi thứ khác | Xem [`gestalt-and-hierarchy.md`](gestalt-and-hierarchy.md). Mỗi màn, mỗi section landing có đúng một điểm nhìn |
| **Cân bằng** | Hai bên màn có "khối lượng thị giác" tương đương | Đối xứng cho trang trang trọng (đăng nhập, chứng nhận). Bất đối xứng cho hầu hết màn: khối nặng 7–8 cột bên này, khối nhẹ nhưng dày thông tin 4–5 cột bên kia |
| **Nhịp** | Khoảng cách lặp lại có quy luật | Dùng thang khoảng cách của token (4, 8, 12, 16, 24, 32, 48…). Khoảng giữa section > khoảng giữa nhóm > khoảng trong nhóm |
| **Tương phản tỉ lệ** | Thứ to cạnh thứ nhỏ, thứ đặc cạnh thứ thoáng | Một ảnh lớn cạnh danh sách gọn; số 40 px cạnh nhãn 13 px. Mọi thứ cỡ trung bình là màn nhạt |
| **Căn lề** | Mọi mép thẳng hàng với một đường nào đó | Ít đường căn nhất có thể. Đếm số đường căn trái khác nhau: quá 3 trên một màn là lộn xộn |

## 2. Khối lượng thị giác

Thứ có khối lượng lớn hơn kéo mắt mạnh hơn và cần đối trọng:

- Nền đậm nặng hơn nền nhạt; ảnh nặng hơn chữ; chữ đậm nặng hơn chữ thường.
- Thứ ở xa tâm nặng hơn cùng thứ đó ở gần tâm (đòn bẩy).
- Hình phức tạp nặng hơn hình đơn giản.

Áp dụng: card nổi bật nền đậm ở cột trái thì cột phải cần một biểu đồ hoặc danh sách dày, không phải một
câu chữ mỏng. Nếu không có gì đủ nặng, thu card nổi bật về toàn hàng thay vì để hụt một bên.

## 3. Landing: mỗi section một hình

Landing nhàm nhất là chuỗi section cùng một khuôn: tiêu đề giữa, ba card ngang, lặp lại. Hãy đổi **hình**
của section theo nội dung nó mang:

| Nội dung | Hình phù hợp |
|---|---|
| Lời hứa chính | Lệch 7 + 5: chữ lớn bên trái, ảnh hoặc sản phẩm thật bên phải |
| Ba lý do | Lưới 3 cột, nhưng mỗi ô có số hoặc ảnh riêng, không chỉ icon và hai dòng |
| Quy trình | Dòng thời gian ngang hoặc bậc thang chéo |
| Bằng chứng | Dải số liệu toàn bề ngang (P26), rồi một lời chứng thực lớn (P17) |
| Bảng giá | Ba cột bằng nhau (P23), gói gợi ý nổi bằng viền |
| Lời mời cuối | Dải màu thương hiệu (P25) |

Đổi nhịp nền: trắng, nhạt, trắng, đậm. Không quá một section nền đậm ngoài dải lời mời cuối.

## 4. Màn app: bố cục theo nhiệm vụ

- Hành động chính nằm trong vùng ngón cái chạm tới (nửa dưới màn điện thoại), hoặc góc trên phải trên desktop.
- Thông tin đọc nhiều đặt trên, thông tin tra cứu đặt dưới hoặc trong vùng phụ.
- Màn chi tiết: đầu trang toàn bề ngang rồi chia 8 + 4. Màn danh sách: bộ lọc rồi bảng.

## 5. Dấu hiệu bố cục "mặc định"

Các dấu hiệu sau cho biết màn được xếp theo quán tính chứ không được thiết kế:

- Mọi section cùng chiều cao, cùng khoảng cách, cùng căn giữa.
- Mọi card cùng cỡ dù nội dung khác tầm quan trọng.
- Ảnh luôn bên phải, chữ luôn bên trái, lặp mãi.
- Không có chỗ nào thật to hoặc thật nhỏ.

Khi thấy một trong số đó, quay lại khối kế hoạch thị giác trong [`CRAFT.md`](../CRAFT.md) và chọn lại
"một điểm táo bạo".

## Nguồn

- Rudolf Arnheim, *Art and Visual Perception*, chương Cân bằng.
- Josef Müller-Brockmann, *Grid Systems in Graphic Design*.
- Robin Williams, *The Non-Designer's Design Book*: bốn nguyên tắc tương phản, lặp lại, căn lề, gần nhau.
- Ellen Lupton, *Graphic Design: The New Basics*, phần nhịp và tỉ lệ.
