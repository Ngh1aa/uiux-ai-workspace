# Common UI/UX Agent Rubric — V5

Mỗi dimension chấm 0–4. Task-specific rubric trong `tasks/*.json` vẫn là nguồn chấm chính; rubric này là common cross-check.

## 1. User & business alignment — 15%
- 0: giao diện trang trí, không giải task.
- 2: hiểu goal nhưng flow còn generic.
- 4: hierarchy, CTA và flow trace được về user/business outcome.

## 2. UX coherence — 15%
- 0: dead-end/flow lỗi.
- 2: happy path dùng được nhưng edge/state yếu.
- 4: navigation, task flow, feedback, error/empty/loading/recovery hợp lý.

## 3. Visual craft & brand fit — 15%
- 0: generic/template/brand sai.
- 2: tương đối consistent.
- 4: hierarchy, typography, spacing, imagery, motion và component grammar có chủ ý và distinctive khi scope yêu cầu.

For multi-page work, `scripts/template-monotony-detector.py` provides a deterministic cross-page structural diversity signal. Identical section sequences across all primary pages or <3 composition families for ≥5 page roles is a strong indicator of score ≤2.

## 4. System quality — 10%
- 0: hardcode/duplicate/one-off.
- 2: có reuse nhưng contract chưa rõ.
- 4: reusable tokens/components/states, ít duplication, maintainable và không tạo design drift.

Template monotony (all pages using the same hero+cards+CTA shell) is a system quality problem even if each instance is well-coded. Use `scripts/template-monotony-detector.py` to validate cross-page composition diversity.

## 5. Inclusive/responsive quality — 10%
- 0: unusable trên viewport/keyboard chính.
- 2: responsive/accessibility cơ bản.
- 4: mobile behavior, semantics, focus, contrast, motion, critical assistive-tech needs được xử lý theo scope.

## 6. Web quality — 10%
SEO/performance/security/privacy/content preservation theo scope.

## 7. Evidence & verification discipline — 15%
- 0: claim không nguồn/test hoặc giả evidence.
- 2: có checks nhưng provenance/limitations yếu.
- 4: claim traceable, test method phù hợp, verified/unverified và limitations rõ.

## 8. Outcome & reliability — 10%
- 0: gọi đẹp hơn là UX tốt hơn; một run gọi là reliable.
- 2: có metric/eval nhưng chưa nối whole journey hoặc sample nhỏ.
- 4: success defined, meaningful outcomes measured, repeated evals used where reliability matters.

## Hard fail

Dù score cao vẫn fail nếu:
- phá primary user task;
- xóa content/URL quan trọng trong redesign mà không migration plan;
- tạo inaccessible critical interaction;
- giả mạo evidence/test/research result;
- tuyên bố WCAG conformance từ partial/automated-only audit;
- tuyên bố UX improvement mà không có outcome evidence phù hợp;
- tuyên bố agent reliable từ một trial;
- vi phạm explicit brand/security/privacy constraint.
