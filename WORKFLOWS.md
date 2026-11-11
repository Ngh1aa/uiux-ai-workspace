# Chọn workflow theo cỡ việc

**Đây là nguồn định tuyến duy nhất:** việc lớn cỡ nào và cần làm những bước gì. Danh sách skill của mỗi cỡ dưới đây là đủ; nếu một skill
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
| Sản phẩm đã có code, và được nhờ "thiết kế lại", "làm lại", "nâng cấp" giao diện? | Ít nhất **L**, cộng track **Redesign sản phẩm có code** (mục 3) |

| Cỡ | Ví dụ | Thời gian điển hình |
|---|---|---|
| **XS** Micro | Đổi màu nút, sửa khoảng cách, sửa chữ | < 1 giờ |
| **S** Component | Thêm trạng thái lỗi cho form, làm lại card, thêm trạng thái rỗng | nửa ngày |
| **M** Màn hình / tính năng | Luồng đặt lịch 3 màn hình, landing page, trang pricing, màn hình cài đặt | 1–3 ngày |
| **L** Khu vực sản phẩm | Làm lại phần giới thiệu ban đầu và trang chủ app, làm lại website 8 trang | 1–3 tuần |
| **XL** Sản phẩm mới | App mới từ con số 0, dựng design system | 3+ tuần |

Không chắc? Chọn cỡ lớn hơn một bậc cho phần **nghiên cứu và cấu trúc**, giữ cỡ nhỏ cho phần **thị giác**.

## 2. Workflow theo cỡ

Mỗi workflow có: bước làm, skill cần đọc (chỉ đọc đúng những file này), sản phẩm phải giao và
ngưỡng chất lượng theo [rubric](skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md).

### XS — Micro và S — Component, trạng thái

XS: sửa ở tầng token hoặc component, kiểm mọi nơi dùng chung, chụp trước và sau. S: liệt kê đủ trạng thái,
dựng từ token, viết chữ cho lỗi và trạng thái rỗng. Bước chi tiết: [workflows/XS-S.md](workflows/XS-S.md).

- Skill: [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md); S thêm
  [`state-feedback-and-error-recovery`](skills_UIUX/state-feedback-and-error-recovery/SKILL.md),
  [`ux-writing-and-microcopy`](skills_UIUX/ux-writing-and-microcopy/SKILL.md).
- Ngưỡng: XS không hard-fail; S các chiều liên quan ≥ 3/5, không hard-fail.

### M — Màn hình / tính năng

Đường đọc trước khi dựng: START-HERE → AGENTS → TASTE → CRAFT → [FLOW](FLOW.md) → trang này → bốn
SKILL.md dưới đây. Reference, pattern và nền tảng chỉ mở đúng phần cần khi quyết định phát sinh
(`python scripts/reading-paths.py` đo độ dài đường đọc).

1. **Khung vấn đề** (1 trang): người dùng là ai, việc chính, câu "Làm sao để", kết quả đo được.
   Brief chỉ nêu giải pháp, hoặc chưa ai biết người dùng là ai, thì chạy
   [`design-thinking-lite`](skills_UIUX/design-thinking-lite/SKILL.md) ở mức M.
2. **Bối cảnh và nội dung trước**: ba câu người dùng ở đâu, vội thế nào, sợ gì khi bấm.
   Viết chữ, số, đối tượng, trạng thái tiếng Việt thật; dữ liệu minh hoạ ghi rõ và vẫn khớp xuyên luồng.
   **Luồng** theo [FLOW.md](FLOW.md): đường chính và ít nhất 2 nhánh lỗi/khôi phục phù hợp tác vụ.
3. **Kiểm kê màn hình × trạng thái** trước khi vẽ.
4. **Khung dây** (wireframe) và đi thử 5 kịch bản. Sửa lỗi trải nghiệm trước khi tô màu.
5. **Thị giác**: áp design system và [thư viện pattern](design-system/patterns/README.md); dựng 2–3
   hướng cho màn quyết định chính rồi qua **cổng duyệt hướng** (dưới đây) trước khi làm các màn còn lại.
6. **Dựng và phản biện** theo rubric, sửa, dựng lại. Bấm thử luồng theo mục *Kiểm trước khi giao* của
   [FLOW.md](FLOW.md) và ghi riêng với soát giao diện; `taste-check` không chứng minh luồng đúng.
7. **Bàn giao**: đặc tả trạng thái, token, hành vi tương tác.

- Skill: [`ux-structure-and-flow-design`](skills_UIUX/ux-structure-and-flow-design/SKILL.md) ·
  [`visual-design-direction`](skills_UIUX/visual-design-direction/SKILL.md) ·
  [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md) ·
  [`design-critique-and-rationale`](skills_UIUX/design-critique-and-rationale/SKILL.md)
- Bắt buộc: [`CRAFT.md`](CRAFT.md) và khối kế hoạch thị giác của nó trước bước 5. Cần chi tiết hơn
  thì mở [craft standards](skills_UIUX/ui-craft-and-visual-qa/references/craft-standards.md).
- Mobile thêm: [`mobile-app-design`](skills_UIUX/mobile-app-design/SKILL.md) và dòng nền tảng ở mục 3.
- Web thêm: dòng nền tảng tương ứng ở mục 3, và một playbook đúng ngành của khách trong
  [`industry-playbooks`](skills_UIUX/industry-playbooks/SKILL.md) (không có thì bỏ qua).
- Mẫu tài liệu: [`templates/ux/`](skills_UIUX/templates/ux/README.md) (khung vấn đề, luồng việc, đặc tả khung dây,
  [duyệt hướng](skills_UIUX/templates/ux/direction-approval.md)).
- Giao: luồng, bảng màn hình × trạng thái, màn đã dựng ở 2 cỡ, bảng rubric, ghi chú bàn giao.
- Ngưỡng: trung bình ≥ 3.5, không chiều nào < 3, không hard-fail.

#### Cổng duyệt hướng (M, L, XL)

Đổi hướng sau khi đã dựng mười màn tốn gấp nhiều lần đổi khi mới có một màn. Vì vậy:

1. Dựng 2–3 hướng trên **cùng** màn quyết định chính, cùng nội dung thật, cùng khung. Các hướng phải khác
   nhau về bản chất (thứ bậc, mật độ, giọng thị giác), không chỉ khác màu.
2. Ghi vào [mẫu duyệt hướng](skills_UIUX/templates/ux/direction-approval.md): mỗi hướng phục vụ việc chính
   ra sao, đánh đổi gì, rủi ro gì, và hướng được đề xuất kèm lý do.
3. Đưa người quyết định (khách, chủ sản phẩm) xem ảnh chụp, **dừng** các màn còn lại cho tới khi có câu trả lời.
4. Không có ai để hỏi (đề chuẩn, làm thử, khách vắng) thì đi tiếp với hướng đề xuất, ghi trạng thái
   `CHƯA DUYỆT` trong mẫu và trong ghi chú giao. Không ghi là đã duyệt khi chưa ai chọn.

Với L và XL, hướng được duyệt mới là đầu vào cho bước "Thử trên 3 màn hình khác bản chất".

### L — Khu vực sản phẩm, làm lại

Như **M**, cộng: đánh giá hiện trạng và 3–5 sản phẩm tham chiếu, kiến trúc thông tin cho cả khu vực, hướng
thị giác thử trên 3 màn khác bản chất, critique 3 vòng. Bước chi tiết: [workflows/L-XL.md](workflows/L-XL.md).

- Sản phẩm đã có code: [`brownfield-redesign`](skills_UIUX/brownfield-redesign/SKILL.md) là bắt buộc.
- Skill thêm: [`website-audit-and-redesign`](skills_UIUX/website-audit-and-redesign/SKILL.md) hoặc
  [`mobile-app-design`](skills_UIUX/mobile-app-design/SKILL.md),
  [`design-reference-research-and-benchmark`](skills_UIUX/design-reference-research-and-benchmark/SKILL.md),
  [`information-architecture`](skills_UIUX/information-architecture/SKILL.md),
  [`research-lite`](skills_UIUX/design-thinking-lite/references/research-lite/README.md) khi thiếu hiểu biết người dùng.
- Ngưỡng: trung bình ≥ 4, không chiều nào < 3.5, không hard-fail.

### XL — Sản phẩm mới / chưa có design system

Như **L**, cộng khám phá, nguyên tắc trải nghiệm, track Design System chạy song song và kế hoạch kiểm chứng
(chi tiết trong [workflows/L-XL.md](workflows/L-XL.md)).

- Skill thêm: [`audience-intent-and-top-tasks`](skills_UIUX/audience-intent-and-top-tasks/SKILL.md),
  [`experience-principles-and-signature-moments`](skills_UIUX/experience-principles-and-signature-moments/SKILL.md),
  [`design-system-and-components`](skills_UIUX/design-system-and-components/SKILL.md).
- Ngưỡng: như L, cộng design system qua `validate.py`.

## 3. Track theo nền tảng và track đặc thù

Bảng chọn; cách làm và lưu ý của từng track ở [workflows/tracks.md](workflows/tracks.md).

| Khi | Đọc thêm |
|---|---|
| iOS, Android | [`ios-app-design`](skills_UIUX/mobile-app-design/references/ios/README.md), [`android-app-design`](skills_UIUX/mobile-app-design/references/android/README.md) và spec sheet của nền tảng |
| Web marketing | [`responsive-and-device-strategy`](skills_UIUX/responsive-and-device-strategy/SKILL.md) |
| Web app, dashboard | [`data-tables-and-enterprise-ux`](skills_UIUX/data-tables-and-enterprise-ux/SKILL.md), [`data-visualization-and-dashboard-ux`](skills_UIUX/data-visualization-and-dashboard-ux/SKILL.md) |
| Chỉ review, audit | [rubric](skills_UIUX/design-critique-and-rationale/references/quality-bar-rubric.md), [`ux-laws-and-heuristics`](skills_UIUX/design-critique-and-rationale/references/ux-laws/README.md) |
| Cải thiện UI đang có | [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md#cải-thiện-giao-diện-hiện-có) |
| Redesign sản phẩm có code | [`brownfield-redesign`](skills_UIUX/brownfield-redesign/SKILL.md) |
| Soát prototype | [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md#soát-prototype) |
| Design system | [`design-system-and-components`](skills_UIUX/design-system-and-components/SKILL.md) |
| Portfolio | [`design-reference-research-and-benchmark`](skills_UIUX/design-reference-research-and-benchmark/SKILL.md) |
| AI trong sản phẩm | [`human-ai-interaction-design`](skills_UIUX/human-ai-interaction-design/SKILL.md) |

## 4. Định nghĩa "xong" chung cho mọi cỡ

- Dự án khách hàng có brand brief; `python3 design-system/scripts/check-brand.py` với `brand.css` không còn lỗi.
- Màn mới mượn cấu trúc từ [starter kit](design-system/starter/README.md) và
  [mẫu theo loại màn](design-system/starter/PATTERNS.md), nhưng mang thương hiệu của dự án.
- [`taste-check.cjs`](skills_UIUX/ui-craft-and-visual-qa/scripts/README.md#soát-theo-gu-taste-checkcjs) không còn
  lỗi ở 390 và 1280 px (website thêm 768 và 1440); desktop và artboard đạt thêm `--layout strict`. Không chạy
  được thì chạy `static-check.cjs`, soát bằng mắt theo README công cụ QA và ghi rõ.
- Đã **nhìn ảnh chụp trang đã dựng**; đủ trạng thái liên quan (rỗng, đang tải, lỗi, nội dung dài, chữ lớn, tối).
- Luồng đạt [FLOW.md](FLOW.md), `flow-check` không có lỗi chắc chắn; luồng bắt buộc FAIL hoặc UNKNOWN chặn
  kết luận Đạt.
- Contrast và vùng chạm đạt [`CRAFT.md`](CRAFT.md); rubric đạt ngưỡng của cỡ việc, không hard-fail.
- Ghi rõ điều gì **chưa** kiểm chứng (người dùng thật, thiết bị thật, trình đọc màn hình).
- M trở lên: hướng thị giác đã qua cổng duyệt, hoặc ghi `CHƯA DUYỆT`. L, XL có duyệt độc lập theo
  [hồ sơ ảnh](skills_UIUX/design-critique-and-rationale/references/independent-review.md).
- Lỗi mới checker và rubric đều không bắt được thì ghi vào [`TASTE-LOG.md`](TASTE-LOG.md).
- Redesign sản phẩm có code: `overlay-check.py` không còn lỗi, test hành vi xanh trước và sau, ADN được giữ
  hoặc người quyết định đã chọn bỏ.
