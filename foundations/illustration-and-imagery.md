# Ảnh, minh hoạ và icon

Dùng ảnh hay minh hoạ, giữ đồng bộ thế nào, làm gì khi chưa có ảnh thật. Hướng nghệ thuật ở skill
[`asset-media-and-art-direction`](../skills_UIUX/asset-media-and-art-direction/SKILL.md); cắt ảnh ở
[`media-crop-and-layout-integrity`](../skills_UIUX/media-crop-and-layout-integrity/SKILL.md).

## 1. Ảnh hay minh hoạ

Ảnh thật khi cần niềm tin (người, sản phẩm, nơi thật) hoặc người dùng cần thấy thứ họ sẽ nhận. Minh hoạ cho
khái niệm trừu tượng, trạng thái rỗng, lỗi, onboarding. Không trộn hai thứ trong một khối.

## 2. Hệ minh hoạ đồng bộ

Chốt sáu thông số trước khi vẽ: nét (đều 2 px đầu tròn, hoặc chỉ mảng), màu (thang thương hiệu và xám, tối đa
3 bậc mỗi hình), hình khối (bo theo bán kính card), phối cảnh (phẳng, không trộn isometric), người (có hay không,
tỉ lệ cố định), mức chi tiết (bằng nhau ở cùng cỡ). **Hoạ tiết và minh hoạ không bao giờ đè lên chữ** (TASTE).

## 3. Ảnh

- Tỉ lệ theo vai trò: 16:9 bìa, 4:3 card, 1:1 chân dung và sản phẩm; khai báo `aspect-ratio`.
- Chủ thể trong 60% giữa khung; chỉnh `object-position` khi lệch.
- Cùng nhiệt độ màu và độ tương phản giữa các ảnh.
- Chữ trên ảnh có lớp phủ đạt 4,5:1 ở chỗ ảnh sáng nhất.
- `alt` nói điều ảnh nói trong ngữ cảnh; ảnh trang trí `alt=""`. Có `width`, `height`, `loading="lazy"`.
- Định dạng AVIF hoặc WebP, nhiều cỡ qua `srcset`.

## 4. Khi chưa có ảnh thật

Dùng khối nền đúng tỉ lệ từ token `media`, không ảnh stock lạc tông, không ảnh AI cho người thật hay bằng chứng.
Ghi ảnh còn thiếu ("thao tác vuốt gốm, 4:3", asset `MISSING`) **trong phần bàn giao, không ghi chú trên màn**.

## 5. Icon

Một bộ cho cả sản phẩm: lưới 24 px, nét 1,75 px bo tròn (`design-system/components/icons.svg`). Cỡ 16 với chữ
13–14, 20 với chữ 15–17, 24 cho điều hướng. Nút chỉ có icon có `aria-label`. Không icon giống nhau ở mọi dòng.
Bottom nav điện thoại: tab đang chọn là viên có icon và nhãn, tab khác chỉ icon (TASTE); ví dụ
[Sai/Đúng, mục G](examples/README.md).

Nguồn chính: Material 3 *Imagery* và *Icons*, W3C *WAI Images Tutorial*, web.dev *CLS*.
