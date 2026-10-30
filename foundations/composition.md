# Bố cục và nhịp

Làm sao màn trông có chủ ý, không phải các khối xếp lần lượt. Phần đo đạc ở
[`layout-and-density.md`](layout-and-density.md); trang này lo cảm nhận.

## 1. Năm công cụ

| Công cụ | Làm cụ thể |
|---|---|
| Điểm nhìn | Mỗi màn, mỗi section landing đúng một điểm nhìn |
| Cân bằng | Đối xứng cho màn trang trọng; còn lại bất đối xứng: khối nặng 7–8 cột, khối nhẹ nhưng dày thông tin 4–5 cột |
| Nhịp | Chỉ dùng thang token (4, 8, 12, 16, 24, 32, 48); giữa section > giữa nhóm > trong nhóm |
| Tương phản tỉ lệ | Thứ to cạnh thứ nhỏ: số 40 px cạnh nhãn 13 px. Mọi thứ cỡ trung bình là màn nhạt |
| Căn lề | Ít đường căn nhất; quá ba đường căn trái khác nhau trên một màn là lộn xộn |

Khối lượng thị giác: nền đậm nặng hơn nền nhạt, ảnh nặng hơn chữ, thứ xa tâm nặng hơn. Card nổi bật nền đậm
bên trái thì bên phải cần biểu đồ hoặc danh sách dày; không có thì cho card nổi bật chiếm cả hàng.

## 2. Chữ ký thị giác: điều lượt benchmark 30/10 thiếu

Lượt 2026-10-30-fresh qua hết checker nhưng chủ repo nhận xét "xấu quá". Dấu hiệu chung: màu trầm an toàn,
card viền mảnh, mọi thứ cỡ vừa, không có chỗ nào đáng nhớ. Trước khi dựng, chốt:

1. **Một ý tưởng hình ảnh lấy từ ngành** (sổ hẹn của phòng khám, vạch sân cầu lông, men gốm) và cho nó
   xuất hiện ở hình khối, không chỉ ở một hình minh hoạ.
2. **Một chỗ thật to** và phần còn lại lùi hẳn về. Chênh lệch cỡ, không chênh lệch màu.
3. **Bỏ bớt** viền, khung, nhãn phụ cho tới khi màn chỉ còn những thứ phải có.

Khi chủ repo gửi màn đã duyệt, đối chiếu với các màn đó trước, không đối chiếu với starter.

## 3. Landing: mỗi section một hình

| Nội dung | Hình |
|---|---|
| Lời hứa | Lệch 7 + 5: chữ lớn và sản phẩm thật |
| Ba lý do | Lưới 3 cột, mỗi ô một số hoặc ảnh riêng, không chỉ icon và hai dòng |
| Quy trình | Dòng thời gian ngang hoặc bậc thang |
| Bảng giá | Ba cột bằng nhau, gói gợi ý nổi bằng viền |
| Lời mời cuối | Dải màu thương hiệu |

Đổi nhịp nền trắng, nhạt, trắng, đậm; không quá một section nền đậm ngoài dải lời mời.

## 4. Dấu hiệu bố cục "mặc định"

Mọi section cùng chiều cao và căn giữa; mọi card cùng cỡ dù khác tầm quan trọng; ảnh luôn bên phải; không có
chỗ nào thật to hay thật nhỏ. Thấy một dấu hiệu thì quay lại kế hoạch thị giác trong [`CRAFT.md`](../CRAFT.md).

Nguồn chính: Arnheim *Art and Visual Perception*, Robin Williams *The Non-Designer's Design Book*.
