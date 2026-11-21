# Bắt đầu từ đây

Repo giúp thiết kế website/app đúng tác vụ, thương hiệu và chất lượng. Đây là cửa vào;
[WORKFLOWS.md](WORKFLOWS.md) là nguồn định tuyến duy nhất, quyết định thứ tự và tài liệu cần mở.

1. Đọc yêu cầu và [AGENTS.md](AGENTS.md). Dùng [brand brief](BRAND-BRIEF.template.md) hiện có;
   thiếu thì ghi giả định, chỉ hỏi khi chặn công việc. Design system khách hàng có ưu tiên.
2. Chọn cỡ và track trong WORKFLOWS. Đọc TASTE; từ S thêm CRAFT; từ M thêm FLOW theo bảng đọc ở đó.
3. Chỉ mở skill và reference theo điều kiện. Nội dung thật và bối cảnh người dùng có trước bố cục.
4. Dựng tại nguồn, tái dùng component/token đang có. Qua cổng hướng trước khi nhân rộng.
5. Soát source, render và hành vi riêng. Mở ảnh mobile/desktop sáng/tối, sửa rồi kiểm lại.
6. Giao ngắn: thay đổi, kiểm tra, bằng chứng, giới hạn. Chưa kiểm ghi `UNKNOWN`, không suy PASS.

Chỉ dùng để thiết kế thì clone nông theo lệnh trong [README](README.md).
Ba lệnh dùng ở mọi dự án: `node scripts/doctor.cjs` kiểm máy trước khi làm;
`node scripts/new-project.cjs <thư mục> --kind <loại>` tạo khung dự án; `node scripts/design-check.cjs <trang.html>`
chạy mọi checker ở bước 5 (`CHECKER_PASS` chưa phải Đạt). Chi tiết và fallback:
[README công cụ QA](skills_UIUX/ui-craft-and-visual-qa/scripts/README.md).
Chuẩn hành vi và mẫu ghi kết quả ở [FLOW.md](FLOW.md); rubric không thay thế kiểm luồng.
M trở lên dùng [review packet](skills_UIUX/design-critique-and-rationale/references/independent-review.md);
agent độc lập vẫn là heuristic. Duyệt của con người chưa có phải ghi `CHƯA DUYỆT`.
