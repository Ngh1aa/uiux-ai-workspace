# Brand brief: <tên khách hàng>

Bước 0 của mọi dự án khách hàng, làm trước khi vẽ (xem [`START-HERE.md`](START-HERE.md)).
Claude điền từ những gì chủ repo hoặc khách đưa: file, link, ảnh chụp, lời mô tả. Thiếu thì ghi
`CHƯA CÓ` kèm giả định, không bịa. Chép file này thành `BRAND-BRIEF.md` trong thư mục dự án, hoặc
dán phần đã điền vào đầu cuộc trò chuyện.

Chi tiết cách xử lý từng mức bằng chứng: skill [`brand-guidelines`](skills_UIUX/brand-guidelines/SKILL.md)
(chỉ cần mục 1, 4, 6, 7).

## 1. Khách đưa gì?

Chọn một mức. Mức quyết định Claude được tự quyết tới đâu.

| Mức | Khách có | Claude làm |
|---|---|---|
| **A** | Brand guideline hoặc design system chính thức | Theo đúng; chỉ bổ sung phần số còn thiếu và ghi `ĐỀ XUẤT` |
| **B** | Một phần: logo, vài màu, font | Giữ nguyên phần có; suy ra phần thiếu và ghi rõ |
| **C** | Chỉ có logo | Rút màu và hình khối từ logo; đề xuất phần còn lại |
| **D** | Không có gì | Đề xuất hướng và đưa 2 phương án cho chủ repo chọn trước khi làm tiếp |

Mức: `?`  Khách đã có design system riêng (Figma, code)? `có / không`. Nếu có: dùng của khách,
repo này chỉ dùng làm checklist chất lượng.

## 2. Sản phẩm

- Khách hàng, ngành:
- Làm gì: `website / app iOS / app Android / web app` (một hay nhiều):
- Người dùng chính, việc chính họ cần làm:
- Ngôn ngữ nội dung: `tiếng Việt / tiếng Anh / cả hai`
- Có dark mode không:

## 3. Logo

- File (ưu tiên SVG): 
- Biến thể (màu, trắng, đen, icon):
- Nền nào dùng được, nền nào không:

## 4. Màu

| Màu | Hex | Nguồn (guideline, logo, web cũ, đề xuất) | Vai trò |
|---|---|---|---|
| | | | màu chính / nhấn / nền / chữ |

Màu logo không mặc nhiên là màu nút. Màu chính không đạt tương phản thì giữ cho logo và
mảng trang trí, tạo thêm một sắc đậm hơn cho chữ và nút, ghi `ĐỀ XUẤT VÌ TƯƠNG PHẢN`.

## 5. Chữ

- Font chính thức: `tên` hoặc `CHƯA CÓ`
- Font dùng trên màn (tiêu đề / thân):

Nội dung tiếng Việt thì font phải có bộ chữ tiếng Việt. Đã kiểm qua dữ liệu Fontsource (10/2026):

- **Có tiếng Việt:** Be Vietnam Pro, Manrope, Plus Jakarta Sans, Space Grotesk, Bricolage Grotesque,
  Lexend, IBM Plex Sans, Inter, Fraunces, Playfair Display, Lora, Literata, Merriweather.
- **Không có tiếng Việt:** DM Sans, Outfit, Instrument Sans. Không dùng cho nội dung tiếng Việt.
- Font khác: kiểm subset `vietnamese` trên Google Fonts hoặc Fontsource, rồi gõ thử
  "Ước mơ Đường phố Hữu Nghị Ỹ Ở" ở cỡ tiêu đề và cỡ thân để xem dấu có bị cắt không.

Không mặc định Be Vietnam Pro hay Inter cho mọi khách: chọn font hợp tính cách thương hiệu.

## 6. Giọng điệu

- Ba tính từ mô tả thương hiệu:
- Điều không bao giờ được (ví dụ: không dùng tiếng lóng, không dùng chữ IN HOA để hét):

## 7. Tham khảo

- Thích (2–3 link hoặc ảnh, kèm lý do thích):
- Không thích (1–2, kèm lý do):

## 8. Dấu ấn riêng của dự án

Đổi ít nhất 3 thứ ngoài màu so với starter kit
(xem [`SIGNATURE.md`](design-system/starter/SIGNATURE.md)):

- Hình khối, bo góc:
- Mật độ, khoảng thở:
- Ảnh hoặc minh hoạ (ảnh khách cung cấp, ảnh stock có giấy phép, hay khung giữ chỗ có ghi chú):
- Kiểu icon:
- Chuyển động:
- Vật gốc của ngành dùng làm hoạ tiết:

## 9. Chốt hướng

Bốn đến sáu dòng tóm hướng thiết kế, và ba điểm khác starter kit. Mức D thì chủ repo duyệt dòng
này trước khi vẽ.

---

## Từ brief sang `brand.css`

1. Chép [`design-system/starter/brand.css`](design-system/starter/brand.css) vào thư mục dự án.
   Giá trị trong đó chỉ là chỗ giữ chỗ, thay hết.
2. Điền màu theo **vai trò**: `--ds-action-primary-bg` là nút chính, `--ds-surface-brand-strong` là
   card nổi bật, `--ds-text-brand` là chữ thương hiệu. Cần thêm màu hover, pressed và bản tối thì
   tự suy từ màu chính và ghi `ĐỀ XUẤT`.
3. Hai khối tối (`@media` và `[data-theme="dark"]`) phải giống hệt nhau.
4. Điền hình khối và font theo mục 5 và 8.
5. Soát rồi sửa tới khi không còn lỗi:

   ```sh
   python3 design-system/scripts/check-brand.py <thư-mục-dự-án>/brand.css
   ```
