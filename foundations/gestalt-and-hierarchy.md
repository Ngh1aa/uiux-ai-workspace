# Nhóm và thứ bậc thị giác

Mắt gom các thứ trên màn thành nhóm và đọc theo thứ tự nào. Đọc khi màn "rối mà không biết vì sao"
hoặc phải giải thích một quyết định bố cục.

## 1. Nhóm: khoảng cách trước, khung sau, màu cuối

| Quy luật | Dùng thế nào | Lỗi hay gặp |
|---|---|---|
| Gần nhau | Nhãn sát ô của nó; giữa nhóm ≥ 1,5 lần trong nhóm | Nhãn cách đều ô trên và ô dưới |
| Giống nhau | Cùng loại thì cùng màu, hình, cỡ; cùng loại card thì giống hệt nhau | Màu thương hiệu cho cả nút, liên kết, tiêu đề, trang trí |
| Vùng chung | Card, khối nền nhạt bao một nhóm | Card lồng card lồng card |
| Liên tục | Cột căn trái thẳng hàng; stepper; dòng thời gian | Mỗi khối căn một kiểu |
| Hình và nền | Sheet, modal có lớp phủ đủ đậm | Nền và card gần cùng độ sáng |
| Khép kín | Hàng cuộn ngang để card cuối bị cắt mép, báo còn nữa | Card vừa khít khung, không ai biết cuộn được |

Khoảng cách không tốn gì; khung và màu tốn sự chú ý. Ví dụ: [Sai/Đúng, mục B](examples/README.md).

## 2. Thứ bậc

Màn tốt trả lời "nhìn 3 giây thấy gì". Đòn bẩy từ mạnh tới yếu: cỡ, độ đậm và tương phản, màu, vị trí
(trên trước dưới, trái trước phải), khoảng trống quanh nó, hình ảnh.

- **Tối đa hai đòn bẩy cho điểm nhìn.** Số vừa to, vừa đậm, vừa màu, vừa viền, vừa icon là đang hét.
- **Ba tầng:** một điểm nhìn; ba tới bảy thứ ở tầng khung đọc (tiêu đề vùng, số phụ, hành động chính);
  còn lại là chi tiết. Tầng hai quá bảy thứ cùng độ nặng thì chia vùng lại.
- Màu nhấn chỉ ở đúng chỗ quan trọng nhất; ví dụ màn tổng quan: card nổi bật và một cột biểu đồ.

Ví dụ: [Sai/Đúng, mục A và I](examples/README.md).

## 3. Tự kiểm

- Làm mờ ảnh chụp (8–12 px): thứ còn thấy phải là tầng 1 và 2.
- Bỏ hết màu: thứ bậc sụp nghĩa là đang dựa vào màu quá nhiều.
- Đếm điểm nhấn (màu nhấn, chữ đậm lớn): hơn ba trên một màn điện thoại là quá nhiều.
- Cho người khác nhìn 5 giây, hỏi "màn này để làm gì, bấm đâu".

`taste-check` bắt một phần: `flat-scale`, `colors`, `highlight`. Phần còn lại phải nhìn.

Nguồn chính: Wertheimer (1923), Palmer *Common region* (1992), Colin Ware *Information Visualization*.
