# Màu: vai trò, OKLCH và tương phản

Trang này trả lời: **dựng bảng màu cho một thương hiệu thế nào để đẹp, đều, đủ tương phản ở cả hai chế độ?**
Đọc khi điền `brand.css` cho dự án mới, khi thêm một màu, hoặc khi chế độ tối trông "bẩn".

## 1. Màu theo vai trò, không theo tên

Giao diện không dùng "màu xanh ngọc"; nó dùng "nền nút chính", "chữ phụ", "viền ô nhập lỗi". Repo chia
ba tầng (xem [`design-system/README.md`](../design-system/README.md)):

| Tầng | Ví dụ | Ai dùng |
|---|---|---|
| Nguyên thuỷ (primitive) | `color.jade.700`, `color.neutral.100` | Chỉ tầng ngữ nghĩa trỏ tới |
| Ngữ nghĩa (semantic) | `action.primary.bg`, `text.secondary`, `dataviz.categorical-1` | Component, pattern, màn |
| Component | `button.height.md`, `field.border` | Chỉ component đó |

Đổi thương hiệu là đổi tầng ngữ nghĩa trong `brand.css`. Chế độ tối chỉ đổi tầng ngữ nghĩa. Không bao giờ
viết mã màu trực tiếp trong CSS của màn: `validate.py` và `check-brand.py` sẽ bắt.

## 2. Vì sao OKLCH

Trong sRGB và HSL, hai màu cùng "độ sáng 50%" có thể trông chênh nhau rất xa (vàng sáng hơn hẳn xanh dương).
OKLCH mô tả màu bằng ba số gần với cách mắt cảm nhận:

- **L** (lightness, 0–1): độ sáng cảm nhận. Hai màu cùng L trông sáng như nhau.
- **C** (chroma, 0–khoảng 0,37): độ rực. 0 là xám.
- **H** (hue, 0–360°): sắc. Khoảng 25 đỏ, 85 vàng, 145 xanh lá, 165–180 ngọc, 250 xanh dương, 300 tím.

Lợi ích thực tế:

1. **Thang đều.** Giữ H cố định, đi L theo bậc đều: bậc 500 của mọi màu sáng ngang nhau, nên đổi màu
   thương hiệu không phá tương phản.
2. **Đoán trước được tương phản.** Chênh L lớn thì tương phản lớn; chọn cặp chữ và nền bằng L trước, rồi
   mới kiểm số.
3. **Chế độ tối có cùng vai trò.** Chọn lại L và C cho từng vai trò, giữ ý nghĩa và sắc thương hiệu;
   không đảo máy móc mọi bậc (700 thành 300).

Giới hạn: màn hình sRGB không hiện được mọi màu OKLCH. Màu rực ở L cao hoặc thấp bị cắt ra ngoài gam màu;
công cụ phải giảm C cho tới khi màu nằm trong sRGB.

## 3. Dựng thang cho thương hiệu mới

```sh
python3 design-system/scripts/oklch-scale.py --hue 165 --chroma 0.14
python3 design-system/scripts/oklch-scale.py --hue 165 --chroma 0.14 --json brand   # nhóm DTCG để dán vào tokens
```

Công cụ giữ H, đi L theo 11 bậc (50 tới 950), cho C cao ở giữa và thấp ở hai đầu, rồi giảm C ở bậc nào
vượt gam sRGB. Cách chọn tham số:

| Tham số | Cách chọn |
|---|---|
| `--hue` | Lấy H của màu logo (dán mã hex vào oklch.com để đọc H) |
| `--chroma` | 0,04–0,08 cho thương hiệu trầm, sang; 0,12–0,16 cho app thông thường; 0,18–0,22 cho thương hiệu trẻ, rực |

Sau đó gán vai trò. Điểm xuất phát an toàn cho nền sáng:

| Vai trò | Bậc |
|---|---|
| Nền nút chính, liên kết | 700 (chữ trắng trên nó đạt 4,5:1) |
| Card nổi bật | 800 hoặc 900 |
| Nền nhạt thương hiệu | 50 hoặc 100 |
| Chữ thương hiệu trên nền nhạt | 700 (800 nếu thang có C cao) |
| Chế độ tối: nút chính | 300, chữ tối trên nó |

Cuối cùng chạy `python3 design-system/scripts/check-brand.py <dự án>/brand.css`: mọi cặp trong
`contrast-pairs.json` được kiểm ở cả hai chế độ.

## 4. Tương phản tối thiểu

| Cái gì | Tối thiểu | Ghi chú |
|---|---|---|
| Chữ thân, chữ dưới 24 px (hoặc dưới 19 px đậm) | 4,5:1 | WCAG 2.2 mức AA, tiêu chí 1.4.3 |
| Chữ lớn | 3:1 | |
| Viền ô nhập, icon mang nghĩa, màu biểu đồ | 3:1 | Tiêu chí 1.4.11, so với nền kề bên |
| Chữ gợi ý (placeholder) trong repo | 4,5:1 | Chặt hơn WCAG, vì người dùng vẫn phải đọc |

Tương phản đạt chưa chắc đã dễ chịu: chữ đen tuyền trên trắng tuyền dễ chói ở chế độ tối. Repo dùng
xám ấm ở cả hai đầu.

## 5. Chế độ tối

- Chốt thứ bậc **page → vùng nhóm → phần nổi** trước: page trầm, phần nổi sáng hơn vừa đủ,
  viền nhẹ để nhận cạnh. Bóng trên nền tối thường không đủ phân tầng. Nền đen OLED có thể phù hợp
  với nền tảng/brand; kiểm viền và chữ thay vì cấm màu đen tuyệt đối.
- Giữ màu theo vai trò: chữ chính, chữ phụ, nền nút, focus, selected và error có token riêng.
  Không dùng opacity cho cả container vì chữ và icon cũng bị giảm tương phản.
- Giảm C của accent sáng khi thấy chói trên render; đổi L trước khi tăng bão hoà.
  Không làm sáng mọi card hoặc tô màu mọi trạng thái cùng lúc.
- Trạng thái có chữ/icon ngoài màu. Kiểm riêng default, hover, focus, selected, disabled và lỗi:
  màu trạng thái đạt tương phản không có nghĩa focus-ring hoặc viền input đã đạt.
- Biểu đồ giữ đơn vị, trục và chú giải có ích; màu dữ liệu không đảo nghĩa giữa hai mode.
  Kiểm đường mảnh trên nền chart, tooltip và series đang chọn, không chỉ cặp màu trong token.
- Ảnh sản phẩm và chân dung giữ màu trung thực. Chỉ dùng bản tối riêng hoặc lớp nền khi cần;
  không áp `filter: brightness()` cho mọi ảnh vì có thể che chi tiết quyết định.
- Tôn trọng lựa chọn hệ thống; khi có nút đổi theme thì lưu lựa chọn của người dùng. Không chớp
  nền sáng lúc tải. Kiểm input, select, dialog và scrollbar với `color-scheme` đúng.

Ví dụ sai: đảo `#fff` thành `#000`, giữ nguyên accent rực và chỉ chạy contrast trên body.
Ví dụ đúng: dùng cùng semantic role ở hai mode, nhìn cạnh sheet, trạng thái bảng và focus ở
390/1280 px; đối chiếu [màn bảng dữ liệu](../design-system/examples/data-table/README.md).

Kiểm máy gồm contrast token, tải font/ảnh, console và reflow. Nhìn ảnh thật để đánh giá độ chói,
thứ bậc bề mặt; chưa kiểm thiết bị thật hoặc người dùng thì ghi `UNKNOWN`.

## 6. Bao nhiêu màu là đủ

- Một màu thương hiệu, một thang xám, bốn màu trạng thái. Thêm màu thứ hai cho thương hiệu chỉ khi brand
  brief yêu cầu.
- Một màn điện thoại không quá ba nhóm màu (`taste-check` cảnh báo `colors`).
- Biểu đồ dùng nhóm `dataviz`, không mượn màu trạng thái (đỏ trong biểu đồ dễ bị đọc là "lỗi").

## Nguồn

- Björn Ottosson, *A perceptual color space for image processing* (2020), định nghĩa Oklab và OKLCH.
- W3C, *CSS Color Module Level 4*, hàm `oklch()`.
- W3C, *WCAG 2.2*, tiêu chí 1.4.3, 1.4.6, 1.4.11.
- Evil Martians, *OKLCH in CSS: why we moved from RGB and HSL* (2022).
