# Starter kit

Bộ khung để bắt đầu thiết kế app hoặc trang web theo đúng gu trong [`TASTE.md`](../../TASTE.md),
dựng trên token và component của design system này. Phong cách lấy từ dự án app giáo vụ:
nền xám lạnh, card trắng phẳng bo 24px, một card navy nổi bật mỗi màn, thanh tab nổi.

| File | Là gì |
|---|---|
| [`mobile.html`](mobile.html) | 7 màn app mẫu: trang chủ, danh sách, chi tiết, biểu mẫu, rỗng, đang tải, lỗi |
| [`web.html`](web.html) | Trang quản trị mẫu, co giãn từ máy tính xuống điện thoại |
| [`PATTERNS.md`](PATTERNS.md) | Quy tắc bố cục cho từng loại màn |
| [`brand.css`](brand.css) | Lớp thương hiệu: màu, nền, bo góc. Đổi thương hiệu thì sửa file này |
| [`app.css`](app.css) | Khối bố cục app mà design system chưa có. Không chứa mã màu |
| [`icons-app.svg`](icons-app.svg) | Icon bổ sung, cùng kiểu với `components/icons.svg` |
| [`inline-icons.py`](inline-icons.py) | Nhúng đúng những icon trang đang dùng vào trang |

## Bắt đầu một dự án

1. Chép `mobile.html` hoặc `web.html` sang dự án, giữ thứ tự nạp CSS:
   `fonts.css` → `tokens.css` → `components.css` → `brand.css` → `app.css`.
2. Sửa `brand.css` theo thương hiệu của dự án, cả khối sáng lẫn khối tối.
3. Với mỗi màn cần làm, chọn loại màn trong [`PATTERNS.md`](PATTERNS.md), chép khối `.app-phone`
   tương ứng, rồi thay nội dung. Giữ cấu trúc, đừng thêm card nổi bật thứ hai.
4. Thêm hoặc bớt icon xong thì chạy:

   ```sh
   python3 design-system/starter/inline-icons.py <trang.html>
   ```

5. Soát trước khi giao (cần Playwright):

   ```sh
   node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs <trang.html> --screenshot qa/
   ```

   Sửa hết lỗi, xem lại từng cảnh báo, rồi **mở ảnh chụp ra nhìn**.

## Giới hạn

- Đây là bản mẫu HTML/CSS để thiết kế và làm prototype, không phải code app native.
- Landing page và website giới thiệu cần hướng nghệ thuật riêng cho từng dự án, nên không có
  khuôn sẵn ở đây. Dùng skill [`visual-design-direction`](../../skills_UIUX/visual-design-direction/SKILL.md)
  và [`landing-page`](../../skills_UIUX/landing-page/SKILL.md).
- Mọi tên người, mã số và con số trong màn mẫu là dữ liệu giả.
