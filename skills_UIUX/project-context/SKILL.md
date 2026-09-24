---
name: project-context
description: |
  Đọc cấu hình `.uiux-profile.json`, project metadata, delivery policy, constraints và các file source-of-truth
  trước khi audit, thiết kế hoặc sửa code trong một project đã cài skills_UIUX. Dùng khi quyết định
  brand/style/IA/component/implementation để generic skill không ghi đè quy ước riêng của project.
---

# Project Context

## Goal

Biến cấu hình riêng của từng repository thành lớp context đứng giữa yêu cầu user và generic UI/UX skills.

## Workflow

1. Tìm `.uiux-profile.json` tại repository root.
2. Nếu file không tồn tại, tiếp tục với các skill đã cài và **không tự bịa project constraints**. Với website work, fallback delivery policy là `adaptive-prompt-os-v4` từ `DEFAULT-WEBSITE-DELIVERY-POLICY.md` trừ khi user/project truth nói khác.
3. Đọc `delivery_policy`, `project`, `source_of_truth` và `constraints` nếu có.
4. Nếu `delivery_policy` không được khai báo trong profile schema v2, dùng `adaptive-prompt-os-v4` làm default cho website work; không tự ghi đè một policy project đã khai báo rõ.
5. Đọc các file trong `source_of_truth` theo đúng thứ tự khai báo khi chúng liên quan task hiện tại.
6. Tóm tắt internal project contract trước khi ra quyết định lớn về IA, visual, design system hoặc code architecture, bao gồm execution lane (`full Prompt OS` hay `lightweight`) khi task là website work.
7. Khi rule xung đột, ưu tiên theo thứ tự:
   - yêu cầu hiện tại của user;
   - `.uiux-profile.json`;
   - source-of-truth documents của project;
   - `DEFAULT-WEBSITE-DELIVERY-POLICY.md`;
   - specialist/domain skill;
   - generic skill defaults.
8. Không tự sửa source-of-truth document chỉ để hợp thức hóa implementation; nếu cần đổi, nêu rationale và thay đổi có chủ đích.

## Delivery-policy rules

- `adaptive-prompt-os-v4` là default cross-project cho website work.
- Substantial build/redesign/multi-page/journey/whole-site work dùng Prompt OS 0→4 theo `DEFAULT-WEBSITE-DELIVERY-POLICY.md`.
- Local/component low-risk work dùng smallest safe lane; không manufacture full phase artifacts nếu không cần.
- Lightweight task phải escalate khi phát hiện shared-owner, structural, cross-route, production/high-risk hoặc art-direction concern.
- Project/user override được phép khi explicit và evidence-backed; không silently hạ system-reality, evidence, release authorization hoặc rendered-inspection rules.

## Source-of-truth rules

- Không assume file tồn tại chỉ vì config khai báo; kiểm tra trước khi dùng.
- Không duplicate nguyên brand guideline/content dài vào code comments.
- Existing tokens/components/architecture đã được project chốt phải được reuse trước khi tạo variant mới.
- Nếu source documents mâu thuẫn nhau, xác định file authoritative nhất theo config/user context và ghi lại conflict.

## Acceptance criteria

- [ ] Project-specific constraints được đọc trước thay đổi lớn.
- [ ] `delivery_policy` đã được resolve cho website task.
- [ ] Source-of-truth liên quan task đã được tham chiếu.
- [ ] Generic skill không ghi đè brand/architecture riêng vô lý.
- [ ] Không invent project facts khi config thiếu.
- [ ] Execution lane phù hợp scope/risk thay vì luôn full hoặc luôn lightweight.
