# Gu thiết kế

Đây là các nguyên tắc chủ repo đã yêu cầu ở những dự án trước. Áp dụng từ bản đầu tiên.
Khi một yêu cầu của dự án cụ thể khác với file này, làm theo dự án và ghi lại lý do.

File này do chủ repo sở hữu: thêm, sửa hoặc xoá dòng nào tuỳ ý. Mỗi dòng nên ngắn và kiểm
tra được bằng mắt.

## Phong cách chung

- Minimalism, hiện đại, nhiều khoảng thở.
- Không rối màu. Màu nhấn chỉ dùng cho thứ thật sự quan trọng, không highlight tràn lan.
- Mỗi màn có **một** thông tin chính rõ ràng; phân cấp chính, phụ phải nhìn ra ngay.
- Không nhồi quá nhiều thông tin trong một màn. Thừa thì tách màn hoặc thu gọn.

## Card và bố cục

- Card bo góc tròn, **đồng nhất** bán kính trên toàn bộ sản phẩm.
- Font, cỡ chữ và bố cục chọn theo chức năng của từng màn, không rập một khuôn cho mọi màn.
- Card nổi bật (nền navy, chữ trắng) dùng để làm điểm nhấn cho thông tin quan trọng nhất.
  Tối đa một card như vậy mỗi màn; màn nào đã ổn thì giữ nguyên, không bắt buộc màn nào cũng có.

## Chữ trên màn

- Ngắn gọn, xúc tích. Không viết câu mô tả nếu giao diện đã tự nói lên.
- **Không nối cụm từ bằng " · "** (kiểu "Text A · Text B · Text C"). Viết lại theo nghĩa:
  tách bằng khoảng trắng, xuống dòng có chủ đích, dùng từ nối, hoặc viết thành câu.
- Không xuống dòng vô cớ. Nếu chữ bị gãy dòng, thu nhỏ cỡ chữ hoặc rút bớt ký tự.

## Trước khi giao

Chạy script soát, nó kiểm tự động phần lớn danh sách dưới đây trên trang đã render:

```sh
node skills_UIUX/ui-craft-and-visual-qa/scripts/taste-check.cjs <trang.html> --screenshot qa/
```

- [ ] Script không còn lỗi; từng cảnh báo đã xem và sửa hoặc có lý do giữ.
- [ ] Không còn dấu " · " nối cụm từ trong nội dung.
- [ ] Không còn chữ gãy dòng ngoài ý muốn, không còn dòng cuối chỉ có một chữ.
- [ ] Mỗi màn có tối đa một card nổi bật.
- [ ] Bán kính bo góc thống nhất giữa các card.
- [ ] Đã mở ảnh chụp ra nhìn từng màn, cả sáng và tối nếu có.
- [ ] Che tên sản phẩm vẫn nhận ra ngành (xem `design-system/starter/SIGNATURE.md`).
