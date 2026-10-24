# Starter kit

Bộ khung để bắt đầu thiết kế app hoặc trang web theo đúng gu trong [`TASTE.md`](../../TASTE.md),
dựng trên token và component của design system này. Phong cách lấy từ dự án app giáo vụ:
nền xám lạnh, card trắng phẳng bo 24px, một card navy nổi bật mỗi màn, thanh tab nổi.

| File | Là gì |
|---|---|
| [`mobile.html`](mobile.html) | 8 màn app mẫu: trang chủ, danh sách, chi tiết, biểu mẫu, rỗng, đang tải, lỗi, chọn nhanh |
| [`web.html`](web.html) | Trang quản trị mẫu, co giãn từ máy tính xuống điện thoại |
| [`web-states.html`](web-states.html) | Trạng thái từng khối của trang web: đang tải, dữ liệu cũ, lỗi, rỗng |
| [`SIGNATURE.md`](SIGNATURE.md) | Cách tạo dấu ấn riêng cho từng dự án, để màn không chỉ là starter kit đổi màu |
| [`PATTERNS.md`](PATTERNS.md) | Quy tắc bố cục cho từng loại màn |
| [`brand.css`](brand.css) | Lớp thương hiệu: màu, nền, bo góc. Đổi thương hiệu thì sửa file này |
| [`app.css`](app.css) | Khối bố cục app mà design system chưa có. Không chứa mã màu |
| [`icons-app.svg`](icons-app.svg) | Icon bổ sung, cùng kiểu với `components/icons.svg` |
| [`inline-icons.py`](inline-icons.py) | Nhúng đúng những icon trang đang dùng vào trang |

## Bắt đầu một dự án

1. Chép `mobile.html` hoặc `web.html` sang dự án, giữ thứ tự nạp CSS:
   `fonts.css` → `tokens.css` → `components.css` → `brand.css` → `app.css`.
2. Sửa `brand.css` theo thương hiệu của dự án, cả khối sáng lẫn khối tối, rồi tạo dấu ấn riêng
   theo [`SIGNATURE.md`](SIGNATURE.md): đổi ít nhất 3 thứ ngoài màu.
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

## Dự án đã có design system

Starter kit dùng cho dự án mới. Dự án đã có bộ token, component và màn đã được duyệt thì **giữ
design system của dự án** (xem thứ tự ưu tiên trong [`AGENTS.md`](../../AGENTS.md)):

1. Không chép `mobile.html` hay `web.html` đè lên dự án. Chỉ dùng [`PATTERNS.md`](PATTERNS.md) làm
   quy tắc bố cục cho từng loại màn, dựng bằng class và token sẵn có của dự án.
2. Đối chiếu token của dự án với vai trò trong `brand.css` (nền, card, chữ phụ, màu nhấn, cảnh báo,
   bán kính). Vai trò nào dự án chưa có thì thêm vào design system của dự án, không nạp `brand.css`.
3. Thành phần mới (bảng, biểu đồ, bước) thêm vào design system của dự án và ghi lại trên trang tài
   liệu của nó, để các màn sau dùng chung.
4. Dấu ấn riêng: xem mục "Dự án đã có nhận diện" trong [`SIGNATURE.md`](SIGNATURE.md).
5. Vẫn chạy `taste-check` trên màn đã dựng. Trang không có `data-screen` (ví dụ file artboard của
   canvas thiết kế) thì chỉ định khung màn bằng `--screen <selector>`.

## Giới hạn

- Đây là bản mẫu HTML/CSS để thiết kế và làm prototype, không phải code app native.
- Landing page và website giới thiệu cần hướng nghệ thuật riêng cho từng dự án, nên không có
  khuôn sẵn ở đây. Dùng skill [`visual-design-direction`](../../skills_UIUX/visual-design-direction/SKILL.md)
  và [`landing-page`](../../skills_UIUX/landing-page/SKILL.md).
- Mọi tên người, mã số và con số trong màn mẫu là dữ liệu giả.
