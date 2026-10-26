# Gestalt và thứ bậc thị giác

Trang này trả lời: **mắt người gom và xếp thứ tự các thứ trên màn như thế nào, và dùng điều đó ra sao?**
Đọc khi màn "rối mà không biết vì sao", khi nhóm các khối, hoặc khi phải giải thích một quyết định bố cục
trong buổi duyệt.

## 1. Sáu nguyên lý Gestalt dùng hằng ngày

Gestalt là các quy luật mắt tự gom chi tiết thành nhóm trước khi đọc từng chữ. Người dùng không nghĩ về
chúng, nên màn đi ngược chúng sẽ bị đọc sai mà không ai nói ra được lý do.

| Nguyên lý | Mắt hiểu thế nào | Dùng trong giao diện | Lỗi thường gặp |
|---|---|---|---|
| **Gần nhau** (proximity) | Thứ đặt gần nhau là một nhóm | Nhãn sát ô nhập của nó; khoảng giữa nhóm lớn hơn khoảng trong nhóm ít nhất 1,5 lần | Nhãn cách đều ô trên và ô dưới, người dùng điền nhầm ô |
| **Giống nhau** (similarity) | Thứ cùng màu, cùng hình, cùng cỡ là cùng loại | Mọi liên kết một màu; mọi trạng thái "Đã duyệt" cùng badge | Dùng màu thương hiệu cho cả nút, liên kết, tiêu đề và trang trí: không còn biết cái gì bấm được |
| **Vùng chung** (common region) | Thứ nằm trong một khung là một nhóm | Card, khối nền nhạt, đường kẻ bao | Lồng card trong card trong card: ba lớp khung cho một nhóm |
| **Liên tục** (continuity) | Mắt đi theo đường thẳng hoặc đường cong | Cột căn trái thẳng hàng; dòng thời gian; stepper | Mỗi khối căn một kiểu, mắt phải nhảy |
| **Khép kín** (closure) | Mắt tự nối hình chưa đủ nét | Card cắt mép ở cuối hàng cuộn ngang báo "còn nữa" | Cuộn ngang mà mọi card vừa khít khung: không ai biết có thể cuộn |
| **Hình và nền** (figure–ground) | Mắt tách vật ở trước khỏi nền | Sheet, modal có lớp phủ; card nổi bật trên nền trang | Nền và card gần cùng độ sáng, lớp phủ quá nhạt |

Thứ tự ưu tiên khi nhóm: **khoảng cách trước, rồi mới tới khung, cuối cùng mới tới màu.** Khoảng cách
miễn phí và không thêm nhiễu; khung và màu tốn sự chú ý.

## 2. Thứ bậc thị giác

Thứ bậc là thứ tự mắt đọc: thấy gì đầu tiên, thứ hai, thứ ba. Một màn có thứ bậc tốt trả lời được câu
"nhìn 3 giây thấy gì" mà không cần đọc.

Sáu đòn bẩy tạo thứ bậc, xếp từ mạnh tới yếu:

1. **Cỡ.** Con số hoặc tiêu đề chính lớn hơn chữ thân 1,5–3 lần.
2. **Độ đậm và tương phản.** Chữ đậm, chữ đen trên nền trắng thắng chữ xám.
3. **Màu.** Một màu nhấn duy nhất cho điều quan trọng nhất; nhiều màu nhấn thì không còn gì nổi.
4. **Vị trí.** Trên trước dưới, trái trước phải (với tiếng Việt và các ngôn ngữ đọc trái sang phải).
5. **Khoảng trống quanh nó.** Thứ được chừa khoảng trống chủ động xung quanh trông quan trọng hơn.
6. **Hình ảnh và hình khối.** Ảnh, minh hoạ, hình tròn giữa các hình chữ nhật.

Quy tắc: **mỗi màn dùng tối đa hai đòn bẩy cho điểm nhìn chính.** Con số vừa to, vừa đậm, vừa màu, vừa có
viền, vừa có icon là đang hét.

### Ba tầng là đủ cho hầu hết màn

| Tầng | Là gì | Bao nhiêu |
|---|---|---|
| 1. Điểm nhìn | Câu trả lời cho câu hỏi chính của màn | Một |
| 2. Khung đọc | Tiêu đề vùng, số phụ, hành động chính | Ba tới bảy |
| 3. Chi tiết | Meta, chú thích, nhãn trục, thời gian | Phần còn lại |

Nếu tầng 2 có hơn bảy thứ cùng độ nặng, màn cần chia vùng lại (xem
[`layout-and-density.md`](layout-and-density.md)).

## 3. Cách tự kiểm tra

- **Nheo mắt** hoặc làm mờ ảnh chụp màn (Gaussian 8–12 px). Thứ còn nhìn thấy phải là tầng 1 và tầng 2.
- **Bản xám.** Bỏ hết màu. Nếu thứ bậc sụp, màn đang dựa vào màu quá nhiều, người mù màu sẽ gặp đúng vấn đề đó.
- **Đếm điểm nhấn.** Đếm các thứ có màu nhấn hoặc chữ đậm lớn. Hơn ba trên một màn điện thoại là quá nhiều.
- **Kể lại.** Cho người khác nhìn 5 giây, hỏi "màn này để làm gì, nên bấm đâu". Câu trả lời sai là thứ bậc sai.

`taste-check.cjs` đo được một phần: `flat-scale` bắt thang chữ phẳng, `colors` bắt quá nhiều nhóm màu,
`highlight` bắt hơn một card nổi bật. Phần còn lại phải nhìn bằng mắt.

## 4. Ví dụ sửa

**Trước:** màn tổng quan có 6 card cùng cỡ, mỗi card một màu nền, tiêu đề 17 px, số 20 px.

**Sau:** một card nổi bật (P01) trả lời "hôm nay cần làm gì", ba KPI (P06) cùng nền trắng, biểu đồ (P08)
có một cột nhấn. Màu thương hiệu xuất hiện ở đúng hai chỗ: card nổi bật và cột nhấn.

## Nguồn

- Max Wertheimer, *Laws of Organization in Perceptual Forms* (1923), bản dịch tiếng Anh trong Ellis (1938).
- Stephen Palmer, *Common region: a new principle of perceptual grouping* (1992).
- Nielsen Norman Group, các bài *Proximity Principle in Visual Design*, *Similarity Principle*, *Visual Hierarchy in UX*.
- Colin Ware, *Information Visualization: Perception for Design*, chương về tiền chú ý (pre-attentive processing).
