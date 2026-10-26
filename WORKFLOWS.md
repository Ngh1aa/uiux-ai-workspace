# Chọn workflow theo cỡ việc

Trang này trả lời một câu: **"Việc này lớn cỡ nào, và tôi cần làm những bước gì?"**
Dành cho designer, PM, kỹ sư và AI agent.

**Đây là nguồn định tuyến duy nhất.** Danh sách skill của mỗi cỡ dưới đây là đủ; nếu một skill
gợi ý đọc thêm skill khác thì chỉ đọc khi việc thật sự cần.

Mọi cỡ việc trên dự án khách hàng đều bắt đầu từ brand brief
([`BRAND-BRIEF.template.md`](BRAND-BRIEF.template.md)); việc nhỏ thì đọc lại brief đã có.

> Quy tắc vàng: chọn cỡ **nhỏ nhất** đủ an toàn. Việc nhỏ chạy quy trình lớn là lãng phí;
> việc lớn chạy quy trình nhỏ là nợ thiết kế.

## 1. Xác định cỡ việc trong 30 giây

| Câu hỏi | Nếu "có" |
|---|---|
| Có đổi luồng người dùng, điều hướng hoặc thêm màn hình mới? | Ít nhất **M** |
| Có đổi hơn ~5 màn hình hoặc cả một khu vực sản phẩm? | Ít nhất **L** |
| Sản phẩm mới, hoặc chưa có design system? | **XL** |
| Chỉ sửa một component, một trạng thái, một đoạn chữ? | **XS** hoặc **S** |

| Cỡ | Ví dụ | Thời gian điển hình |
|---|---|---|
| **XS** Micro | Đổi màu nút, sửa khoảng cách, sửa chữ | < 1 giờ |
| **S** Component | Thêm trạng thái lỗi cho form, làm lại card, thêm empty state | nửa ngày |
| **M** Màn hình / tính năng | Luồng đặt lịch 3 màn hình, landing page, trang pricing, màn hình cài đặt | 1–3 ngày |
| **L** Khu vực sản phẩm | Redesign onboarding + home, làm lại website 8 trang | 1–3 tuần |
| **XL** Sản phẩm mới | App mới từ con số 0, dựng design system | 3+ tuần |

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

1. **Khung vấn đề** (1 trang): người dùng là ai, việc chính, kết quả đo được.
2. **Luồng**: happy path + ít nhất 2 nhánh lỗi/khôi phục.
3. **Kiểm kê màn hình × trạng thái** trước khi vẽ.
4. **Wireframe** và walkthrough 5 kịch bản. Sửa lỗi UX trước khi tô màu.
5. **Visual**: áp design system; so 2 phương án cho màn hình quyết định chính.
6. **Render + critique** theo rubric, sửa, render lại.
   Với luồng có dữ liệu, bấm thử từ chọn/nhập → xác nhận → quay lại sửa → xác nhận lại. Đối chiếu
   cùng dữ liệu trên mọi màn (số lượng, biến thể, tổng tiền, ngày giờ); kiểm tra giữ lựa chọn và
   ít nhất một nhánh lỗi/khôi phục. Ghi kết quả riêng với soát giao diện; `taste-check` không
   chứng minh luồng đúng.
7. **Handoff**: spec trạng thái, token, hành vi tương tác.

- Skill: [`ux-structure-and-flow-design`](skills_UIUX/ux-structure-and-flow-design/SKILL.md) ·
  [`visual-design-direction`](skills_UIUX/visual-design-direction/SKILL.md) ·
  [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md) ·
  [`design-critique-and-rationale`](skills_UIUX/design-critique-and-rationale/SKILL.md)
- Bắt buộc: [`CRAFT.md`](CRAFT.md) và khối kế hoạch thị giác của nó trước bước 5. Cần chi tiết hơn
  thì mở [craft standards](skills_UIUX/ui-craft-and-visual-qa/references/craft-standards.md).
- Mobile thêm: [`mobile-app-design`](skills_UIUX/mobile-app-design/SKILL.md) + spec sheet nền tảng (mục 3).
- Web thêm: dòng nền tảng tương ứng ở mục 3, và một playbook đúng ngành của khách trong
  [`industry-playbooks`](skills_UIUX/industry-playbooks/SKILL.md) (không có thì bỏ qua).
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

- Skill thêm: [`audience-intent-and-top-tasks`](skills_UIUX/audience-intent-and-top-tasks/SKILL.md) ·
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
| Web app / dashboard | [Web app patterns](skills_UIUX/ui-craft-and-visual-qa/references/web-app-patterns.md) · [`data-tables-and-enterprise-ux`](skills_UIUX/data-tables-and-enterprise-ux/SKILL.md) · [`data-visualization-and-dashboard-ux`](skills_UIUX/data-visualization-and-dashboard-ux/SKILL.md) | Mật độ cao nhưng quét được; bàn phím là công dân hạng nhất |
| Demo trên trình duyệt cho app | [`mobile-web-preview`](skills_UIUX/mobile-app-design/references/mobile-web-preview/README.md) | Bằng chứng trình duyệt không chứng minh app native |

## 4. Track đặc thù

| Track | Khi nào | Bắt đầu từ |
|---|---|---|
| **Chỉ review / audit** | Cần đánh giá, chưa sửa | [rubric](skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md) + [`ux-laws-and-heuristics`](skills_UIUX/ux-laws-and-heuristics/SKILL.md) |
| **Cải thiện UI đang có** | Sửa/polish giữ brand và hành vi; redesign khi được yêu cầu | Chọn XS–L theo bảng cỡ việc, dùng [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md#cải-thiện-giao-diện-hiện-có); cả site đổi hướng thì dùng L + `website-audit-and-redesign` |
| **Soát prototype** | Bản HTML/CSS/JS cần demo được | Theo cỡ việc tương ứng + [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md#soát-prototype); thử đường demo và ghi tác vụ mô phỏng |
| **Design system** | Thêm token, component, hoặc dựng hệ thống mới | [`design-system/`](design-system/README.md) · [platform mapping](design-system/docs/platform-mapping.md) · [`design-system-and-components`](skills_UIUX/design-system-and-components/SKILL.md) |
| **Portfolio** | Làm lại portfolio / định vị nghề | Như cỡ M, cộng [`design-reference-research-and-benchmark`](skills_UIUX/design-reference-research-and-benchmark/SKILL.md) |
| **AI trong sản phẩm** | Tính năng có AI tạo nội dung/quyết định | [`human-ai-interaction-design`](skills_UIUX/human-ai-interaction-design/SKILL.md) |


## 5. Định nghĩa "xong" chung cho mọi cỡ

- Dự án khách hàng có brand brief; `brand.css` của dự án qua
  `python3 design-system/scripts/check-brand.py` không còn lỗi.
- Màn mới mượn cấu trúc từ [starter kit](design-system/starter/README.md) và theo
  [mẫu theo loại màn](design-system/starter/PATTERNS.md), nhưng mang thương hiệu và dấu ấn của dự án.
- [`taste-check.cjs`](skills_UIUX/ui-craft-and-visual-qa/scripts/README.md#soát-theo-gu-taste-checkcjs)
  không còn lỗi ở cả 390 px và 1280 px (website thêm 768 và 1440). Không chạy được thì làm theo
  mục "Khi không chạy được taste-check" trong [`START-HERE.md`](START-HERE.md) và ghi rõ. Màn desktop
  và artboard canvas đạt thêm `--layout strict` (không còn màn trống, nội dung dồn một bên, card mỏng).
- Đã **nhìn ảnh render thật**, không chỉ đọc code.
- Đủ trạng thái liên quan (rỗng, đang tải, lỗi, nội dung dài, chữ lớn, tối).
- Đã bấm thử tác vụ chính và nhánh quay lại/sửa; dữ liệu đầu vào, tóm tắt và xác nhận khớp nhau.
  Demo không có backend phải ghi rõ hành vi nào chỉ mô phỏng.
- Contrast và vùng chạm đạt chuẩn trong [`CRAFT.md`](CRAFT.md); không chạm mặc định nào trong danh sách
  cấm mà không có lý do từ brief.
- Rubric đạt ngưỡng của cỡ việc, không hard-fail.
- Ghi rõ điều gì **chưa** kiểm chứng (người dùng thật, thiết bị thật, trình đọc màn hình).
