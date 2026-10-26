# Starter kit

Bộ khung để bắt đầu thiết kế app hoặc trang web theo đúng gu trong [`TASTE.md`](../../TASTE.md),
dựng trên token và component của design system này. Cấu trúc màn (bố cục, trạng thái, thứ bậc)
là phần dùng lại được. Bề mặt hiện tại (nền xám lạnh, card trắng bo 24px, card navy nổi bật, lấy từ
một dự án app giáo vụ) chỉ là **chỗ giữ chỗ**: dự án khách hàng thay bằng thương hiệu trong brand
brief ([`BRAND-BRIEF.template.md`](../../BRAND-BRIEF.template.md)).

| File | Là gì |
|---|---|
| [`mobile.html`](mobile.html) | 8 màn app mẫu: trang chủ, danh sách, chi tiết, biểu mẫu, rỗng, đang tải, lỗi, chọn nhanh |
| [`web.html`](web.html) | Trang quản trị mẫu, co giãn từ máy tính xuống điện thoại |
| [`landing.html`](landing.html) | Khung section cho landing page: header, hero, bằng chứng, vấn đề, lợi ích, cách hoạt động, bảng giá, lời khách, câu hỏi, lời mời cuối, footer |
| [`desktop.html`](desktop.html) | 6 khung app desktop 1440 × 900: tổng quan, danh sách và chi tiết, form nhiều bước, chi tiết đối tượng, cài đặt, đăng nhập chia đôi. Dùng cùng [`desktop.css`](desktop.css) |
| [`web-states.html`](web-states.html) | Trạng thái từng khối của trang web: đang tải, dữ liệu cũ, lỗi, rỗng |
| [`SIGNATURE.md`](SIGNATURE.md) | Cách tạo dấu ấn riêng cho từng dự án, để màn không chỉ là starter kit đổi màu |
| [`PATTERNS.md`](PATTERNS.md) | Quy tắc bố cục cho từng loại màn |
| [`brand.css`](brand.css) | Lớp thương hiệu: màu, nền, bo góc. Giá trị hiện tại là chỗ giữ chỗ; dự án chép ra rồi điền theo brand brief |
| [`app.css`](app.css) | Khối bố cục app mà design system chưa có. Không chứa mã màu |
| [`icons-app.svg`](icons-app.svg) | Icon bổ sung, cùng kiểu với `components/icons.svg` |
| [`inline-icons.py`](inline-icons.py) | Nhúng đúng những icon trang đang dùng vào trang |

## Bắt đầu một dự án

1. Chép `mobile.html`, `web.html` hoặc `desktop.html` sang dự án, giữ thứ tự nạp CSS:
   `fonts.css` → `tokens.css` → `components.css` → `brand.css` → `app.css` (→ `desktop.css`).
2. Chép `brand.css` vào dự án và điền theo brand brief, cả khối sáng lẫn hai khối tối (giống hệt
   nhau), rồi soát bằng `python3 design-system/scripts/check-brand.py <dự-án>/brand.css`. Sau đó
   tạo dấu ấn riêng theo [`SIGNATURE.md`](SIGNATURE.md): đổi ít nhất 3 thứ ngoài màu.
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

   Màn desktop và artboard canvas thêm `--width 1440 --height 900 --layout strict`.
   Sửa hết lỗi, xem lại từng cảnh báo, rồi **mở ảnh chụp ra nhìn**.

## Giới hạn

- Đây là bản mẫu HTML/CSS để thiết kế và làm prototype, không phải code app native.
- Landing page và website giới thiệu cần hướng nghệ thuật riêng cho từng dự án. [`landing.html`](landing.html)
  chỉ là **khung section** (thứ tự, việc của từng section, cấu trúc HTML), cố ý để trơn với chữ
  trong [ngoặc]. Hướng thị giác lấy từ [`visual-design-direction`](../../skills_UIUX/visual-design-direction/SKILL.md),
  [`landing-page`](../../skills_UIUX/industry-playbooks/references/landing-page.md) và kế hoạch
  thị giác trong [`CRAFT.md`](../../CRAFT.md).
- Mọi tên người, mã số và con số trong màn mẫu là dữ liệu giả.
