---
name: uiux-workspace
description: Thiết kế, thiết kế lại, cải thiện, soát hoặc review UI/UX cho website, landing page, web app, dashboard và app iOS/Android theo gu và quy trình của repo uiux-ai-workspace. Dùng khi người dùng nhờ thiết kế giao diện, dựng màn hình hay prototype, làm design system, redesign sản phẩm đã có code, hoặc nhắc tới "repo uiux".
---

<!-- uiux-workspace: sinh bởi scripts/link-claude-code.cjs; sửa ở integrations/claude-code/SKILL.template.md rồi chạy lại -->

# Thiết kế UI/UX bằng uiux-ai-workspace

Repo nằm ở `{{REPO}}`. Không làm theo trí nhớ về repo: đọc file hiện tại, vì gu và quy trình được cập nhật thường xuyên.

1. Đọc `{{REPO}}/START-HERE.md` và `{{REPO}}/AGENTS.md`, rồi làm đúng thứ tự trong đó. `WORKFLOWS.md` quyết định
   cỡ việc và những file cần mở; không đọc cả thư viện skill.
2. Trước khi dựng, chạy `node {{REPO}}/scripts/doctor.cjs`. Thiếu công cụ thì sửa theo lời nó in, hoặc ghi
   `UNKNOWN` cho phần không soát được.
3. Dự án mới: `node {{REPO}}/scripts/new-project.cjs <thư mục dự án> --kind <loại>`. Dự án đã có code hoặc đã có
   design system riêng thì theo AGENTS mục 2 và mục 6, không chép starter đè lên.
4. Trước khi giao: `node {{REPO}}/scripts/design-check.cjs <trang.html>`, mở từng ảnh ra nhìn, bấm thử luồng,
   rồi mới kết luận. `CHECKER_PASS` chưa phải Đạt.

Thứ tự ưu tiên khi mâu thuẫn: yêu cầu mới nhất của người dùng, yêu cầu riêng của dự án, `TASTE.md`, rồi tới
skill và quy trình. Không thấy thư mục repo thì nói rõ với người dùng và nhờ chạy lại
`node scripts/link-claude-code.cjs` trong repo; không tự bịa quy tắc thay thế.
