# Chữ cho tiếng Việt

Chọn font, cỡ và khoảng dòng để tiếng Việt đọc dễ, không vỡ dấu. Tiếng Việt có dấu chồng ("ể", "ỗ", "ậ"),
nên nhiều quy tắc viết cho tiếng Anh phải chỉnh lại.

## 1. Chọn font

Font phải qua bốn câu: có đủ bộ dấu không; dấu có được vẽ riêng (hỏi và ngã không chạm nhau) không; dấu chồng
của chữ hoa có lọt khoảng dòng không; có số dạng bảng không. Kiểm bằng chuỗi ở mục 5, vì mức hỗ trợ đổi theo
phiên bản font.

Có sẵn trong repo, chạy offline: **Be Vietnam Pro** (thân, mặc định), **Manrope** và **Source Serif 4**
(xem [fonts](../design-system/fonts/README.md)). Font hiển thị cá tính hơn đặt qua `--app-font-display`.
Theo [`CRAFT.md`](../CRAFT.md), không để Inter, Roboto hay font hệ thống là font duy nhất.

## 2. Cỡ và khoảng dòng

| Vai trò | Token | Cỡ | Khoảng dòng |
|---|---|---|---|
| Hiển thị | `type.display` | 32 | 1,2 |
| Tiêu đề lớn, vừa, nhỏ | `type.title-lg/md/sm` | 24 / 20 / 17 | 1,2 / 1,35 / 1,35 |
| Thân lớn, thân | `type.body-lg/md` | 17 / 15 | 1,6 |
| Thân nhỏ, nhãn | `type.body-sm`, `type.label-*` | 12–14 | 1,5 |

- **Không chữ nào dưới 12 px**, kể cả nhãn tab, trục biểu đồ, badge (TASTE).
- Thân không dưới 1,5: ở 1,3–1,4 dấu dòng dưới chạm chân chữ dòng trên.
- Tiêu đề nhiều dòng từ 1,2; chữ 40 px trở lên xuống 1,05–1,1 được sau khi thử dòng chữ hoa có dấu chồng.
- Ô nhập và nút không cắt dấu: không `overflow: hidden` cùng `line-height: 1`.

Ví dụ: [Sai/Đúng, mục C](examples/README.md).

## 3. Ngắt dòng

- Đoạn văn 60–75 ký tự (12–15 từ). Trình duyệt ngắt ở mọi khoảng trắng, kể cả giữa "Hà / Nội":
  tiêu đề dùng `text-wrap: balance`, đoạn văn `text-wrap: pretty`, cụm không tách ("890.000 ₫", tên riêng)
  nối bằng `&nbsp;`.
- Không `hyphens: auto` cho tiếng Việt.

## 4. Chữ hoa, nghiêng, số

- Chữ hoa toàn bộ chỉ cho nhãn 2–3 từ, giãn +0,04 em. Không dùng nhãn IN HOA nhỏ phía trên mọi tiêu đề.
- Không dùng nghiêng giả; nhấn bằng độ đậm.
- Số: "1.204", "4,8". Tiền: "890.000 ₫" hoặc "đ", một kiểu cho cả sản phẩm. Ngày luôn kèm thứ hoặc ngày tháng
  ("Thứ Sáu 24/10"); danh sách lịch sử chỉ "dd/mm" bên trái. Cột số và số đổi theo thời gian dùng
  `tabular-nums`.

## 5. Chuỗi kiểm font

Dán ở cỡ 13, 15, 17, 24, 40 px, chữ thường và chữ hoa:

```text
Ể Ỗ Ậ Ữ Ờ Ẳ Ẵ Ặ Ừ Ỹ ể ỗ ậ ữ ờ ẳ ẵ ặ ừ ỹ
Nguyễn Thị Hường, Trường Tiểu học Hàng Chiếu, Quảng Ngãi
NGUYỄN THỊ HƯỜNG, TRƯỜNG TIỂU HỌC
1.204.567 ₫  4,8 điểm  26/10/2026 14:20
```

Đạt khi không ký tự nào rơi sang font khác, hỏi và ngã không chạm, dấu chồng chữ hoa không chạm dòng trên.

Nguồn chính: Donny Trương *Vietnamese Typography*, Bringhurst *The Elements of Typographic Style*, MDN `text-wrap`.
