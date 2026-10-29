# Font chạy offline

Be Vietnam Pro vẫn là mặc định. Mở `pairs.css` khi brief cần giọng biên tập:
**Source Serif 4** cho tiêu đề/câu trích, **Manrope** cho nội dung và dữ liệu.
Không thay font hệ thống của ứng dụng native chỉ để giống bản web.

```html
<link rel="stylesheet" href="../../fonts/pairs.css">
```

```css
.editorial { font-family: "Manrope", sans-serif; }
.editorial h1 { font-family: "Source Serif 4", serif; font-optical-sizing: auto; }
```

Hai file variable TTF nguyên bản, không subset hoặc đổi tên family; mỗi thư mục có OFL.
`manifest.json` ghi URL lấy file, ngày lấy và SHA-256 của binary/license.
Probe cmap gồm dấu chồng tiếng Việt và `₫`; kiểm lại với
`python design-system/scripts/check-fonts.py`. Script dùng thư viện chuẩn để đọc cmap Unicode
của TTF; lượt đóng gói còn đối chiếu bằng FontTools trong môi trường công cụ tách khỏi repo.

Lora đã được thử trong phiên nâng cấp nhưng file upstream thiếu `₫`, nên không đóng gói.
Source Serif 4 và Manrope đều có `₫` và ký tự probe. Cmap không chứng minh mọi cỡ chữ đẹp:
xem ảnh specimen trong [màn tham chiếu](../examples/data-table/README.md).
Review thị giác và ưu tiên của chủ repo: `CHƯA DUYỆT`; chưa thử thiết bị native.
