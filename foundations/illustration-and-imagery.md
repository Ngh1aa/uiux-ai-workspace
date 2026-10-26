# Ảnh, minh hoạ và icon

Trang này trả lời: **dùng ảnh hay minh hoạ, giữ chúng đồng bộ thế nào, và làm gì khi chưa có ảnh thật?**
Phần chọn hướng nghệ thuật cho dự án nằm trong skill
[`asset-media-and-art-direction`](../skills_UIUX/asset-media-and-art-direction/SKILL.md); phần cắt ảnh
trong khung nằm trong [`media-crop-and-layout-integrity`](../skills_UIUX/media-crop-and-layout-integrity/SKILL.md).

## 1. Ảnh hay minh hoạ

| Dùng ảnh thật khi | Dùng minh hoạ khi |
|---|---|
| Cần niềm tin: người thật, sản phẩm thật, nơi thật | Khái niệm trừu tượng: bảo mật, đồng bộ, "chưa có dữ liệu" |
| Người dùng cần thấy thứ họ sẽ nhận (khoá học, món ăn, phòng) | Trạng thái rỗng, lỗi, onboarding |
| Thương hiệu dựa vào cảm xúc thật (giáo dục, y tế, du lịch) | Cần đồng bộ tuyệt đối giữa nhiều màn |

Không trộn hai thứ trong cùng một khối. Một sản phẩm có thể có cả hai, nhưng mỗi loại một vai trò rõ.

## 2. Một hệ minh hoạ đồng bộ

Minh hoạ trông "lấy từ năm nguồn" là lỗi phổ biến nhất. Chốt sáu thông số trước khi vẽ hoặc chọn:

| Thông số | Ví dụ quyết định |
|---|---|
| Nét | Nét đều 2 px, đầu tròn; hoặc không nét, chỉ mảng |
| Màu | Chỉ dùng thang thương hiệu và xám, tối đa 3 bậc mỗi hình |
| Hình khối | Bo tròn theo bán kính card của dự án |
| Phối cảnh | Phẳng chính diện; không trộn với isometric |
| Người | Có hoặc không có mặt; tỉ lệ đầu thân cố định |
| Chi tiết | Mức chi tiết bằng nhau ở cùng cỡ hiển thị |

Minh hoạ trạng thái rỗng trong repo (P27) là ví dụ tối giản: hai mảng chồng nhau, một icon, màu từ token.
Đủ để có hình, không cần hoạ sĩ.

## 3. Ảnh

- **Tỉ lệ cố định theo vai trò:** 16:9 cho bìa và video, 4:3 cho card, 1:1 cho chân dung và sản phẩm.
  Khai báo bằng `aspect-ratio` để trang không nhảy khi ảnh tải xong.
- **Chủ thể trong vùng an toàn:** mặt người và sản phẩm nằm trong 60% giữa khung, vì khung sẽ bị cắt khác
  nhau trên điện thoại và desktop. Dùng `object-position` khi chủ thể lệch.
- **Đồng bộ màu ảnh:** cùng nhiệt độ màu, cùng độ tương phản. Ảnh lẫn ấm lạnh trông như ghép từ nhiều nơi.
- **Chữ trên ảnh** cần lớp phủ (scrim) đủ để chữ đạt 4,5:1 ở chỗ ảnh sáng nhất, không chỉ chỗ trung bình.
- **Văn bản thay thế (`alt`)** mô tả điều ảnh nói trong ngữ cảnh đó, không mô tả pixel. Ảnh trang trí để
  `alt=""`.
- **Hiệu năng:** `width`, `height`, `loading="lazy"` cho ảnh dưới màn đầu, định dạng AVIF hoặc WebP, nhiều
  cỡ qua `srcset`.

## 4. Khi chưa có ảnh thật

Không để khối xám trống và không dùng ảnh stock không liên quan. Dùng ảnh giữ chỗ có chú thích (P30):
nền sọc từ token `media`, ghi tỉ lệ và nội dung ảnh cần chụp ("Ảnh 1:1: cận cảnh sản phẩm"). Khách hàng
nhìn vào hiểu ngay cần cung cấp gì, và bản nháp không giả vờ là bản thật.

Ảnh do AI tạo chỉ dùng khi brief cho phép, ghi rõ trong ghi chú giao, và không dùng cho người thật, sản
phẩm thật hay bằng chứng (lời chứng thực, ảnh sự kiện).

## 5. Icon

- Một bộ icon cho cả sản phẩm: cùng lưới 24 px, cùng độ dày nét, cùng kiểu đầu nét. Repo dùng bộ nét 1,75 px
  bo tròn trong `design-system/components/icons.svg`.
- Icon đi kèm chữ, trừ vài icon ai cũng hiểu (đóng, tìm, quay lại) và vẫn phải có `aria-label`.
- Cỡ icon theo cỡ chữ đi cùng: 16 px với chữ 13–14, 20 px với chữ 15–17, 24 px cho thanh điều hướng.
- Icon không phải trang trí cho mọi dòng; danh sách mà dòng nào cũng có icon giống nhau là nhiễu.

## Nguồn

- Nielsen Norman Group, *Photos as Web Content* và *Icon Usability*.
- Material Design 3, *Imagery* và *Icons*.
- W3C, *WAI Images Tutorial* (cây quyết định viết `alt`).
- web.dev, *Optimize Cumulative Layout Shift* và *Serve responsive images*.
