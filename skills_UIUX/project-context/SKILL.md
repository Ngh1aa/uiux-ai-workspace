---
name: project-context
description: |
  Đọc cấu hình `.uiux-profile.json`, project metadata, constraints và các file source-of-truth
  trước khi audit, thiết kế hoặc sửa code trong một project đã cài skills_UIUX. Dùng khi quyết định
  brand/style/IA/component/implementation để generic skill không ghi đè quy ước riêng của project.
---

# Project Context

## Goal

Biến cấu hình riêng của từng repository thành lớp context đứng giữa yêu cầu user và generic UI/UX skills.

## Workflow

1. Tìm `.uiux-profile.json` tại repository root.
2. Nếu file không tồn tại, tiếp tục với các skill đã cài và **không tự bịa project constraints**.
3. Đọc `project`, `source_of_truth` và `constraints` nếu có.
4. Đọc các file trong `source_of_truth` theo đúng thứ tự khai báo khi chúng liên quan task hiện tại.
5. Tóm tắt internal project contract trước khi ra quyết định lớn về IA, visual, design system hoặc code architecture.
6. Khi rule xung đột, ưu tiên theo thứ tự:
   - yêu cầu hiện tại của user;
   - `.uiux-profile.json`;
   - source-of-truth documents của project;
   - specialist/domain skill;
   - generic skill defaults.
7. Không tự sửa source-of-truth document chỉ để hợp thức hóa implementation; nếu cần đổi, nêu rationale và thay đổi có chủ đích.

## Source-of-truth rules

- Không assume file tồn tại chỉ vì config khai báo; kiểm tra trước khi dùng.
- Không duplicate nguyên brand guideline/content dài vào code comments.
- Existing tokens/components/architecture đã được project chốt phải được reuse trước khi tạo variant mới.
- Nếu source documents mâu thuẫn nhau, xác định file authoritative nhất theo config/user context và ghi lại conflict.

## Acceptance criteria

- [ ] Project-specific constraints được đọc trước thay đổi lớn.
- [ ] Source-of-truth liên quan task đã được tham chiếu.
- [ ] Generic skill không ghi đè brand/architecture riêng vô lý.
- [ ] Không invent project facts khi config thiếu.
