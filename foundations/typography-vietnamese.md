# Chữ cho tiếng Việt

Trang này trả lời: **chọn font, cỡ và khoảng dòng thế nào để tiếng Việt đọc dễ và không vỡ dấu?**
Tiếng Việt có dấu chồng (ví dụ "ể", "ỗ", "ậ"), nên nhiều quy tắc chữ viết cho tiếng Anh phải chỉnh lại.

## 1. Chọn font

Một font hợp tiếng Việt phải qua bốn câu hỏi:

1. **Có đủ bộ dấu không?** Gõ thử chuỗi kiểm tra ở mục 6. Thiếu ký tự thì trình duyệt lấy font khác cho
   riêng chữ đó, dòng chữ lẫn hai kiểu.
2. **Dấu có được vẽ riêng cho tiếng Việt không?** Font chỉ ghép dấu tự động thường để dấu hỏi và dấu ngã
   chạm nhau, hoặc dấu lệch khỏi trục chữ.
3. **Dấu chồng có lọt trong khoảng dòng không?** Chữ hoa có dấu chồng ("Ổ", "Ấ") cao hơn chữ hoa thường
   khá nhiều; font có phần trên thấp sẽ bị cắt dấu khi khoảng dòng chật.
4. **Có số dạng bảng (tabular figures) không?** Cần cho bảng, giá, đồng hồ đếm ngược.

Font mặc định của repo là **Be Vietnam Pro** (SIL OFL 1.1), vẽ cho tiếng Việt. Các font khác đã được cộng
đồng dùng nhiều cho tiếng Việt: Inter, Roboto, Noto Sans và Noto Serif, Lexend, Montserrat (bản mới), Manrope,
Plus Jakarta Sans (bản có hỗ trợ tiếng Việt). Luôn kiểm tra bằng chuỗi ở mục 6 trước khi dùng, vì mức hỗ trợ
thay đổi theo phiên bản.

Font hiển thị (tiêu đề lớn, số lớn) có thể cá tính hơn, đặt qua `--app-font-display` trong `brand.css`.
Font thân giữ trung tính và đọc tốt ở 15–17 px.

## 2. Cỡ chữ và khoảng dòng

| Vai trò | Token | Cỡ | Khoảng dòng | Ghi chú |
|---|---|---|---|---|
| Hiển thị | `type.display` | 32 | 1,2 | Số lớn và tiêu đề trang |
| Tiêu đề lớn | `type.title-lg` | 24 | 1,2 | |
| Tiêu đề vừa | `type.title-md` | 20 | 1,35 | |
| Tiêu đề nhỏ | `type.title-sm` | 17 | 1,35 | |
| Thân lớn | `type.body-lg` | 17 | 1,6 | Đọc dài, điện thoại |
| Thân | `type.body-md` | 15 | 1,6 | Mặc định app |
| Thân nhỏ, nhãn | `type.body-sm`, `type.label-*` | 12–14 | 1,5 | Không dưới 12 px |

Ba quy tắc riêng cho tiếng Việt:

- **Khoảng dòng chữ thân không dưới 1,5.** Ở 1,3–1,4, dấu của dòng dưới chạm chân chữ dòng trên.
- **Tiêu đề nhiều dòng từ 1,2.** Chữ hiển thị rất lớn (40 px trở lên) xuống 1,05–1,1 được, sau khi
  đã thử dòng chữ hoa có dấu chồng. Tiêu đề chữ hoa toàn bộ cần 1,3 trở lên.
- **Ô nhập và nút không cắt dấu.** Đó là lý do ô nhập của repo cao 52 px với chữ 17 px. Không đặt
  `overflow: hidden` cùng `line-height: 1` cho chữ có dấu.

## 3. Độ dài dòng và ngắt dòng

- Đoạn văn 60–75 ký tự mỗi dòng (khoảng 12–15 từ tiếng Việt). Trên desktop, vùng chữ rộng hơn thì đặt
  cột phụ bên cạnh thay vì kéo dòng dài ra.
- Tiếng Việt viết từng âm tiết cách nhau, nên trình duyệt ngắt dòng ở mọi khoảng trắng, kể cả giữa hai âm
  tiết của một từ ("Hà / Nội"). Với tiêu đề và nhãn ngắn, dùng `text-wrap: balance`; với đoạn văn, dùng
  `text-wrap: pretty` để tránh dòng cuối chỉ còn một chữ. Cụm không được tách (tên riêng, số và đơn vị như
  "890.000 ₫") nối bằng khoảng trắng không ngắt (`&nbsp;`).
- Không gạch nối tự động (`hyphens: auto`) cho tiếng Việt.

## 4. Chữ hoa, chữ nghiêng, số

- **Chữ hoa toàn bộ** làm dấu chồng cao và khó đọc; chỉ dùng cho nhãn rất ngắn (2–3 từ) với khoảng cách
  chữ +0,04 em trở lên.
- **Chữ nghiêng giả** (font không có bản nghiêng thật) làm dấu lệch. Dùng độ đậm để nhấn thay cho nghiêng.
- **Số:** dấu chấm ngăn nghìn, dấu phẩy thập phân ("1.204", "4,8"). Tiền tệ: "890.000 ₫" hoặc
  "890.000 đ", thống nhất một kiểu trong cả sản phẩm. Ngày "26/10/2026", giờ "14:20".
  Dùng `font-variant-numeric: tabular-nums` cho cột số và số thay đổi theo thời gian.

## 5. Thang chữ

Thang chữ là tỉ lệ giữa các cỡ. Thang 1,2 (mỗi bậc lớn hơn 20%) hợp với app; 1,25–1,333 hợp với landing và
nội dung biên tập. Quan trọng hơn tỉ lệ chính xác là **khoảng cách giữa chữ lớn nhất và chữ thân**: ít nhất
1,5 lần trên desktop, 1,3 lần trên điện thoại (`taste-check` bắt bằng luật `flat-scale`). Xem bảng mật độ
trong [`layout-and-density.md`](layout-and-density.md).

## 6. Chuỗi kiểm tra font

Cặp chữ thử nghiệm chạy offline: [Source Serif 4 + Manrope](../design-system/fonts/README.md).
Dùng serif cho tiêu đề biên tập và sans cho dữ liệu; không đổi font mặc định khi brief không cần.
File đã có probe cmap tiếng Việt và `₫`, hash binary/license; nhìn thêm
[specimen sáng/tối](../design-system/examples/data-table/README.md) trước khi chọn.

Dán chuỗi này vào trang mẫu ở các cỡ 13, 15, 17, 24, 40 px và nhìn ở cả chữ thường lẫn chữ hoa:

```text
Ể Ỗ Ậ Ữ Ờ Ẳ Ẵ Ặ Ừ Ỹ ể ỗ ậ ữ ờ ẳ ẵ ặ ừ ỹ
Nguyễn Thị Hường, Trường Tiểu học Hàng Chiếu, Quảng Ngãi
NGUYỄN THỊ HƯỜNG, TRƯỜNG TIỂU HỌC
1.204.567 ₫  4,8 điểm  26/10/2026 14:20
```

Đạt khi: không có ký tự rơi sang font khác, dấu hỏi và dấu ngã không chạm nhau, dấu chồng của dòng chữ hoa
không chạm dòng trên ở khoảng dòng của dự án.

## Nguồn

- Be Vietnam Pro, The Be Vietnam Pro Project Authors (github.com/bettergui/BeVietnamPro), giấy phép SIL OFL 1.1.
- Vietnamese Typography, tài liệu của Donny Trương (vietnamesetypography.com).
- Robert Bringhurst, *The Elements of Typographic Style*, phần độ dài dòng và thang chữ.
- MDN, *text-wrap* và *font-variant-numeric*.
