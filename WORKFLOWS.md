# Chọn workflow theo cỡ việc

Trang này trả lời một câu: **"Việc này lớn cỡ nào, và tôi cần làm những bước gì?"**
Dành cho designer, PM, kỹ sư và AI agent. Không cần hiểu Flow OS hay Task Contract để dùng.

> Quy tắc vàng: chọn cỡ **nhỏ nhất** đủ an toàn. Việc nhỏ chạy quy trình lớn là lãng phí;
> việc lớn chạy quy trình nhỏ là nợ thiết kế.

## 1. Xác định cỡ việc trong 30 giây

| Câu hỏi | Nếu "có" |
|---|---|
| Có đổi luồng người dùng, điều hướng hoặc thêm màn hình mới? | Ít nhất **M** |
| Có đổi hơn ~5 màn hình hoặc cả một khu vực sản phẩm? | Ít nhất **L** |
| Sản phẩm mới, hoặc chưa có design system? | **XL** |
| Chỉ sửa một component, một trạng thái, một đoạn chữ? | **XS** hoặc **S** |

| Cỡ | Ví dụ | Thời gian điển hình | Flow trong runtime |
|---|---|---|---|
| **XS** Micro | Đổi màu nút, sửa khoảng cách, sửa chữ | < 1 giờ | `micro-ui-change` |
| **S** Component | Thêm trạng thái lỗi cho form, làm lại card, thêm empty state | nửa ngày | `existing-ui-improvement` |
| **M** Màn hình / tính năng | Luồng đặt lịch 3 màn hình, trang pricing, màn hình cài đặt | 1–3 ngày | `page-ui-work` · `mobile-app-design` |
| **L** Khu vực sản phẩm | Redesign onboarding + home, làm lại website 8 trang | 1–3 tuần | `professional-website-redesign` · `mobile-app-design` |
| **XL** Sản phẩm mới | App mới từ con số 0, dựng design system | 3+ tuần | `professional-website-redesign` / `mobile-app-design` + track Design System |

Không chắc? Chọn cỡ lớn hơn một bậc cho phần **nghiên cứu và cấu trúc**, giữ cỡ nhỏ cho phần **visual**.

## 2. Workflow theo cỡ

Mỗi workflow có: bước làm, skill cần đọc (chỉ đọc đúng những file này), sản phẩm phải giao và
ngưỡng chất lượng theo [rubric](skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md).

### XS — Micro

1. Tìm token/component đang dùng. Sửa ở **tầng token hoặc component**, không vá CSS cục bộ.
2. Kiểm tra mọi nơi dùng chung component đó.
3. Chụp trước/sau ở mobile + desktop (hoặc hai cỡ app), sáng + tối nếu có dark mode.

- Skill: [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md)
- Giao: ảnh trước/sau + một dòng lý do.
- Ngưỡng: không có hard-fail nào trong rubric.

### S — Component / trạng thái

1. Liệt kê đủ trạng thái: mặc định, hover/pressed, focus, disabled, loading, rỗng, lỗi, nội dung dài.
2. Thiết kế từ token có sẵn; nếu thiếu token thì thêm ở tầng semantic, không hard-code.
3. Viết microcopy cho lỗi và trạng thái rỗng.
4. Render tất cả trạng thái, kiểm contrast và vùng chạm.

- Skill: [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md) ·
  [`state-feedback-and-error-recovery`](skills_UIUX/state-feedback-and-error-recovery/SKILL.md) ·
  [`ux-writing-and-microcopy`](skills_UIUX/ux-writing-and-microcopy/SKILL.md)
- Tham chiếu: [craft standards](skills_UIUX/ui-craft-and-visual-qa/references/craft-standards.md)
- Giao: bảng trạng thái đã render + đặc tả component (anatomy, biến thể, a11y).
- Ngưỡng: các chiều liên quan ≥ 3/5, không hard-fail.

### M — Màn hình / tính năng

1. **Khung vấn đề** (1 trang): người dùng là ai, việc chính, kết quả đo được. Thiếu spec, hoặc sản
   phẩm có nhiều vai trò: theo [khi thiếu spec](skills_UIUX/ux-structure-and-flow-design/references/missing-spec-and-roles.md).
2. **Luồng**: happy path + ít nhất 2 nhánh lỗi/khôi phục.
3. **Kiểm kê màn hình × trạng thái** trước khi vẽ.
4. **Wireframe** và walkthrough 5 kịch bản. Sửa lỗi UX trước khi tô màu.
5. **Visual**: áp design system; so 2 phương án cho màn hình quyết định chính.
6. **Render + critique** theo rubric, sửa, render lại.
7. **Handoff**: spec trạng thái, token, hành vi tương tác.

- Skill: [`ux-structure-and-flow-design`](skills_UIUX/ux-structure-and-flow-design/SKILL.md) ·
  [`visual-design-direction`](skills_UIUX/visual-design-direction/SKILL.md) ·
  [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md) ·
  [`design-critique-and-rationale`](skills_UIUX/design-critique-and-rationale/SKILL.md)
- Mobile thêm: [`mobile-app-design`](skills_UIUX/mobile-app-design/SKILL.md) + spec sheet nền tảng (mục 3).
- Template: [`templates/ux/`](skills_UIUX/templates/ux/README.md) (problem statement, task flow, wireframe spec).
- Giao: flow, bảng màn hình × trạng thái, mockup đã render ở 2 cỡ, bảng rubric, ghi chú handoff.
- Ngưỡng: trung bình ≥ 3.5, không chiều nào < 3, không hard-fail.

### L — Khu vực sản phẩm / redesign

Như **M**, cộng thêm:

1. **Audit hiện trạng** + benchmark 3–5 sản phẩm tham chiếu (trích nguyên tắc, không sao chép bề mặt).
2. **Kiến trúc thông tin** và mô hình điều hướng cho toàn khu vực.
3. **Visual direction**: 4–7 thuộc tính thị giác có biểu hiện cụ thể, ma trận vai trò trang/màn hình.
4. **Thử trên 3 màn hình khác bản chất** trước khi nhân rộng.
5. **Critique 3 vòng** (xem rubric): tự review → review chéo theo vai trò → review "người lạ" chỉ nhìn ảnh.
   Vòng 3 giao cho người hoặc agent chưa thấy quá trình làm, dùng
   [mẫu giao việc](skills_UIUX/design-critique-and-rationale/references/cold-review-prompt.md).
6. Kiểm nhất quán xuyên màn hình (ảnh đặt cạnh nhau).

- Skill thêm: [`website-audit-and-redesign`](skills_UIUX/website-audit-and-redesign/SKILL.md) hoặc
  [`mobile-app-design`](skills_UIUX/mobile-app-design/SKILL.md) ·
  [`design-reference-research-and-benchmark`](skills_UIUX/design-reference-research-and-benchmark/SKILL.md) ·
  [`information-architecture`](skills_UIUX/information-architecture/SKILL.md)
- Giao: tất cả của M + audit, direction, ma trận màn hình, ảnh nhất quán xuyên màn hình.
- Ngưỡng: trung bình ≥ 4, không chiều nào < 3.5, không hard-fail.

### XL — Sản phẩm mới / chưa có design system

Như **L**, cộng thêm:

1. **Discovery**: vấn đề, đối tượng, giả định rủi ro nhất, cách kiểm chứng.
2. **Nguyên tắc trải nghiệm** (3–5 câu, có đánh đổi rõ ràng).
3. **Track Design System** (mục 4) chạy song song từ tuần đầu.
4. **Kế hoạch kiểm chứng** với người dùng thật; khi chưa có người thật thì ghi `PLANNED_VALIDATION`.

- Skill thêm: [`product-discovery`](skills_UIUX/product-discovery/SKILL.md) ·
  [`experience-principles-and-signature-moments`](skills_UIUX/experience-principles-and-signature-moments/SKILL.md) ·
  [`design-system-and-components`](skills_UIUX/design-system-and-components/SKILL.md)
- Ngưỡng: như L, cộng design system qua `validate.py` (contrast, parity sáng/tối).

## 3. Track theo nền tảng

| Nền tảng | Đọc thêm | Lưu ý quan trọng nhất |
|---|---|---|
| iOS | [iOS spec sheet](skills_UIUX/ios-app-design/references/ios-spec-sheet.md) · [`ios-app-design`](skills_UIUX/ios-app-design/SKILL.md) | Dùng control hệ thống trước; Dynamic Type; vuốt-lùi không bao giờ bị chặn |
| Android | [Android spec sheet](skills_UIUX/android-app-design/references/android-spec-sheet.md) · [`android-app-design`](skills_UIUX/android-app-design/SKILL.md) | Edge-to-edge, predictive back, window size classes |
| Cả hai | [Mobile patterns playbook](skills_UIUX/mobile-app-design/references/mobile-patterns-playbook.md) | Chung ý nghĩa, khác "chrome": không ép iOS và Android giống hệt nhau |
| Web marketing | [`responsive-and-device-strategy`](skills_UIUX/responsive-and-device-strategy/SKILL.md) | Mobile không phải desktop thu nhỏ |
| Web app / dashboard (flow `web-app-dashboard`) | [Web app patterns](skills_UIUX/ui-craft-and-visual-qa/references/web-app-patterns.md) · [`data-tables-and-enterprise-ux`](skills_UIUX/data-tables-and-enterprise-ux/SKILL.md) · [`data-visualization-and-dashboard-ux`](skills_UIUX/data-visualization-and-dashboard-ux/SKILL.md) | Mật độ cao nhưng quét được; bàn phím là công dân hạng nhất |
| Demo trên trình duyệt cho app | [`mobile-web-preview`](skills_UIUX/mobile-web-preview/SKILL.md) | Bằng chứng trình duyệt không chứng minh app native |

## 4. Track đặc thù

| Track | Khi nào | Bắt đầu từ |
|---|---|---|
| **Chỉ review / audit** | Cần đánh giá, chưa sửa (review design system thì router tự chọn `design-system-audit`) | Flow `audit-review` / `mobile-app-audit` + [rubric](skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md) + [`ux-laws-and-heuristics`](skills_UIUX/ux-laws-and-heuristics/SKILL.md) |
| **Design system** | Thêm token, component, hoặc dựng hệ thống mới. Flow `design-system-work`; chỉ review thì `design-system-audit` | [`design-system/`](design-system/README.md) · [platform mapping](design-system/docs/platform-mapping.md) · [`design-system-and-components`](skills_UIUX/design-system-and-components/SKILL.md) · [`design-system-governance-and-adoption`](skills_UIUX/design-system-governance-and-adoption/SKILL.md) |
| **Nghiên cứu người dùng** | Cần bằng chứng thật | [`research-evidence-pipeline`](skills_UIUX/research-evidence-pipeline/SKILL.md) · [`user-research-planning-and-recruitment`](skills_UIUX/user-research-planning-and-recruitment/SKILL.md) |
| **Portfolio** | Làm lại portfolio / định vị nghề | Flow `portfolio-career-system` |
| **AI trong sản phẩm** | Tính năng có AI tạo nội dung/quyết định | [`human-ai-interaction-design`](skills_UIUX/human-ai-interaction-design/SKILL.md) |

Mỗi flow là một file trong [`skills_UIUX/flows/`](skills_UIUX/flows/README.md): mở file, đi lần lượt
từng chặng, đọc đúng skill được liệt kê.

## 5. Định nghĩa "xong" chung cho mọi cỡ

- Màn mới bắt đầu từ [starter kit](design-system/starter/README.md) và theo
  [mẫu theo loại màn](design-system/starter/PATTERNS.md).
- [`taste-check.cjs`](skills_UIUX/ui-craft-and-visual-qa/scripts/README.md#soát-theo-gu-taste-checkcjs) không còn lỗi.
- Đã **nhìn ảnh render thật**, không chỉ đọc code.
- Đủ trạng thái liên quan (rỗng, đang tải, lỗi, nội dung dài, chữ lớn, tối).
- Contrast và vùng chạm đạt chuẩn trong [craft standards](skills_UIUX/ui-craft-and-visual-qa/references/craft-standards.md).
- Rubric đạt ngưỡng của cỡ việc, không hard-fail.
- Ghi rõ điều gì **chưa** kiểm chứng (người dùng thật, thiết bị thật, trình đọc màn hình).
