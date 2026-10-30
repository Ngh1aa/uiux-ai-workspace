# Màu: vai trò, OKLCH và tương phản

Dựng bảng màu đẹp, đều, đủ tương phản ở cả hai chế độ. Đọc khi điền `brand.css`, thêm màu, hoặc chế độ
tối trông "bẩn".

## 1. Màu theo vai trò

Ba tầng token: nguyên thuỷ (`color.jade.700`) → ngữ nghĩa (`action.primary.bg`, `text.secondary`) →
component. Đổi thương hiệu và chế độ tối chỉ đổi tầng ngữ nghĩa trong `brand.css`. Không viết mã màu trong CSS
của màn; `validate.py` và `check-brand.py` bắt.

## 2. Dựng thang bằng OKLCH

OKLCH (L độ sáng cảm nhận, C độ rực, H sắc) cho thang đều: cùng L thì sáng ngang nhau, đổi màu thương hiệu không
phá tương phản.

```sh
python3 design-system/scripts/oklch-scale.py --hue 165 --chroma 0.14 [--json brand]
```

| Tham số | Chọn |
|---|---|
| `--hue` | H của màu logo (đọc bằng oklch.com) |
| `--chroma` | 0,04–0,08 trầm, sang; 0,12–0,16 app thường; 0,18–0,22 trẻ, rực |

| Vai trò (nền sáng) | Bậc |
|---|---|
| Nút chính, liên kết | 700 |
| Card nổi bật | 800–900 (TASTE: nút trên card này là nút trắng) |
| Nền nhạt thương hiệu | 50–100 |
| Chế độ tối, nút chính | 300, chữ tối trên nó |

Rồi chạy `check-brand.py <dự án>/brand.css` để kiểm mọi cặp ở cả hai chế độ.

## 3. Tương phản tối thiểu

Chữ thường 4,5:1; chữ ≥ 24 px (hoặc ≥ 19 px đậm) 3:1; viền ô nhập, icon mang nghĩa, màu biểu đồ 3:1 so với nền
kề; placeholder trong repo 4,5:1. Tránh đen tuyền trên trắng tuyền ở chế độ tối.

## 4. Chế độ tối

- Chốt thứ bậc page → vùng → phần nổi; phần nổi sáng hơn vừa đủ, viền nhẹ để nhận cạnh.
- Mọi vai trò (chữ, nền nút, focus, chọn, lỗi) có token riêng; không giảm opacity cả container.
- Giảm C của accent khi chói; đổi L trước khi tăng độ rực.
- Biểu đồ giữ nghĩa màu giữa hai chế độ; **nhãn đặt trực tiếp trên dữ liệu, không dùng chú giải** (TASTE).
- Không chớp nền sáng khi tải; khai báo `color-scheme` để input, select, scrollbar đúng chế độ.
- Kiểm riêng mặc định, hover, focus, đang chọn, bị khoá và lỗi ở cả hai chế độ.
- Không áp `filter: brightness()` cho mọi ảnh; ảnh sản phẩm và chân dung giữ màu thật.
- Có nút đổi giao diện thì lưu lựa chọn của người dùng; không có thì theo hệ thống.

## 5. Bao nhiêu màu

Một màu thương hiệu, một thang xám, các màu trạng thái chỉ khi có trạng thái thật. Một màn không quá **ba nhóm
màu**: trung tính, thương hiệu, một màu cảnh báo. Gom trạng thái vào ba nhóm đó trước khi thêm màu mới; mỗi
trạng thái có chữ hoặc icon đi kèm. Biểu đồ dùng nhóm `dataviz`, không mượn đỏ (đọc thành "lỗi").
Ví dụ: [Sai/Đúng, mục I](examples/README.md).

Nguồn chính: Ottosson *Oklab* (2020), CSS Color 4 `oklch()`, WCAG 2.2 tiêu chí 1.4.3 và 1.4.11.
