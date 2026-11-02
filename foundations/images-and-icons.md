# Ảnh và icon

Mở khi màn có ảnh hoặc cần thêm icon. Tách từ [`CRAFT.md`](../CRAFT.md) mục 4; quy tắc giữ nguyên.

**Ảnh, theo thứ tự ưu tiên**
1. Ảnh khách cung cấp. Hỏi trong brand brief (mục 8).
2. Ảnh stock có giấy phép dùng thương mại (Unsplash, Pexels). Ghi nguồn và tên tác giả trong ghi
   chú giao; không dùng ảnh có người nhận diện được trong ngữ cảnh nhạy cảm.
3. Khung giữ chỗ có ghi chú: khối màu bề mặt, đúng tỉ lệ ảnh thật, chú thích "Ảnh: <mô tả cần
   chụp>". Tốt hơn ảnh stock lạc tông.

Không dùng: ảnh AI tạo người thật hoặc sản phẩm thật trông như ảnh chụp, ảnh lấy từ web khác không
rõ giấy phép, ảnh chèn chữ không đọc được. Ảnh có chữ đè lên phải qua kiểm tra tương phản ở vùng chữ.
Ảnh luôn có `alt` mô tả nội dung (ảnh trang trí: `alt=""`), có `width`/`height` để không nhảy bố cục.

**Icon**
1. Bộ icon của design system khi đủ: `design-system/components/icons.svg` (32 icon) và
   `design-system/starter/icons-app.svg` (11 icon).
2. Thiếu thì lấy từ **Lucide** (ISC) hoặc **Phosphor** (MIT), một bộ cho cả dự án, cùng độ dày nét
   với bộ sẵn có (1,75 px ở 24 px, đầu nét tròn). Chép SVG vào dự án, ghi tên bộ và giấy phép trong ghi chú giao.
   Không chép cả bộ vào repo này.
3. App native: SF Symbols (iOS), Material Symbols (Android).

Cỡ: 16 trong dòng chữ, 20 mặc định, 24 điều hướng. Icon đi kèm nhãn trong điều hướng; nút chỉ có
icon phải có `aria-label`. Không trộn hai bộ icon, không dùng emoji thay icon.
