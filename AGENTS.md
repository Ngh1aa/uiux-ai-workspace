# Quy tắc cho AI làm việc trong repo này

Repo phục vụ một việc: giúp thiết kế website và app đẹp, đúng gu chủ repo. Bắt đầu ở
[`START-HERE.md`](START-HERE.md); file này chỉ ghi các quy tắc luôn áp dụng.

## 1. Làm thật, không chỉ khuyên

Khi việc làm được bằng công cụ hiện có thì làm luôn tới khi ra kết quả xem được, không dừng ở
lời khuyên. Chỉ hỏi lại khi thiếu thông tin thật sự chặn việc và đoán sai sẽ tốn công làm lại.
Còn lại thì chọn giả định hợp lý, nói rõ giả định đó và làm tiếp.

## 2. Thứ tự ưu tiên khi các nguồn mâu thuẫn

1. Yêu cầu mới nhất của chủ repo.
2. Yêu cầu riêng của dự án đang làm (brief, design system của dự án, và phong cách gốc (ADN) của
   sản phẩm đã có, xem [`brownfield-redesign`](skills_UIUX/brownfield-redesign/SKILL.md)).
3. [`TASTE.md`](TASTE.md).
4. Skill và quy trình trong repo này.
5. Tài liệu chính thức (Apple HIG, Material, WCAG), rồi tới nguồn tham khảo khác.

## 3. Nói đúng mức đã kiểm chứng

- Chỉ nói "đã xong", "đạt contrast", "không tràn chữ" khi đã thật sự kiểm tra trên màn đã render.
- Phân biệt rõ: đã kiểm chứng, suy luận, giả định, chưa biết.
- Không bịa số liệu, lời người dùng, đánh giá hay dữ liệu mẫu trông như thật mà không ghi chú.
- Tự đánh giá theo kịch bản thì gọi là "đánh giá theo kịch bản", không gọi là "test với người dùng".

## 4. Thiết kế

- Áp dụng `TASTE.md` ngay từ bản đầu; từ cỡ S, lên kế hoạch thị giác theo `CRAFT.md` trước khi dựng.
- Đọc đúng skill mà cỡ việc hoặc flow chỉ định, không đọc tràn cả thư viện.
- Dựng từ token và component có sẵn. Thiếu thì thêm ở tầng token theo vai trò, không gán cứng màu.
- Đủ các trạng thái liên quan: mặc định, đang tải, rỗng, lỗi, nội dung dài.
- Nhìn ảnh render thật ở cỡ điện thoại và máy tính trước khi giao. Build chạy được không có nghĩa
  là giao diện đẹp.
- Sửa ở đúng tầng gây lỗi: lỗi hướng thiết kế thì sửa hướng, không vá CSS từng chỗ.

## 5. Sửa repo này

Mục này nói về việc sửa chính repo `uiux-ai-workspace`. Làm trên code của dự án khách thì xem mục 6.

- Làm trên nhánh riêng, mở pull request; không force-push lên `main`.
- Giữ thay đổi gọn, đúng phạm vi được nhờ; không tiện tay sửa chỗ khác.
- Không làm yếu test hay kiểm tra chỉ để qua CI.
- Không xoá dữ liệu, nhánh hay file quan trọng khi chưa được yêu cầu.

## 6. Làm trên dự án đã có code

- Yêu cầu "thiết kế lại", "làm lại", "nâng cấp giao diện" là sự cho phép sửa và **xoá** code giao diện
  cũ của dự án trên một nhánh riêng: token, CSS, template, renderer, test đang khoá giao diện cũ. Không
  hỏi lại từng file.
- Thay tại nguồn, không phủ đè: không thêm file CSS nạp sau cùng, không dùng `!important` để thắng
  cascade cũ, không vá DOM bằng JS sau render, không sửa tay file sinh tự động.
- Giữ hành vi, dữ liệu, URL và câu chữ đã kiểm chứng; bảo vệ chúng bằng test trước khi xoá code.
- Giữ ADN thị giác của sản phẩm trừ khi người quyết định chọn bỏ.
- Quy trình đầy đủ: [`brownfield-redesign`](skills_UIUX/brownfield-redesign/SKILL.md).

## 7. Nội dung của bên thứ ba

Trước khi chép file không phải của mình, xem license và
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Không chép hoặc chỉnh sửa nội dung có điều
khoản cấm phân phối lại (ví dụ các skill `docx`, `pdf`, `pptx`, `xlsx` của Anthropic) vào repo.
Không đưa code hay thư viện skill của bên thứ ba vào `main`; dẫn link thay vì chép.

## 8. Khi giao

Báo ngắn gọn: kết quả là gì, đã kiểm tra bằng cách nào, điều gì còn chưa kiểm chứng.
