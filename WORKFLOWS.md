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
| Sản phẩm đã có code, và được nhờ "thiết kế lại", "làm lại", "nâng cấp" giao diện? | Ít nhất **L**, cộng track **Redesign sản phẩm có code** (mục 4) |

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

### XS — Micro

1. Tìm token/component đang dùng. Sửa ở **tầng token hoặc component**, không vá CSS cục bộ.
2. Kiểm tra mọi nơi dùng chung component đó.
3. Chụp trước và sau ở điện thoại và desktop (hoặc hai cỡ app), sáng và tối nếu có chế độ tối.

- Skill: [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md)
- Giao: ảnh trước/sau + một dòng lý do.
- Ngưỡng: không có hard-fail nào trong rubric.

### S — Component / trạng thái

1. Liệt kê đủ trạng thái: mặc định, di chuột, đang nhấn, focus, vô hiệu, đang tải, rỗng, lỗi, nội dung dài.
2. Thiết kế từ token có sẵn; nếu thiếu token thì thêm ở tầng ngữ nghĩa, không viết giá trị cứng.
3. Viết chữ giao diện cho lỗi và trạng thái rỗng.
4. Dựng tất cả trạng thái, kiểm tương phản và vùng chạm.

- Skill: [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md) ·
  [`state-feedback-and-error-recovery`](skills_UIUX/state-feedback-and-error-recovery/SKILL.md) ·
  [`ux-writing-and-microcopy`](skills_UIUX/ux-writing-and-microcopy/SKILL.md)
- Tham chiếu có điều kiện: [craft standards](skills_UIUX/ui-craft-and-visual-qa/references/craft-standards.md)
- Giao: bảng trạng thái đã dựng và đặc tả component (cấu trúc, biến thể, trợ năng).
- Ngưỡng: các chiều liên quan ≥ 3/5, không hard-fail.

### M — Màn hình / tính năng

Đường đọc trước khi dựng: START-HERE → AGENTS → TASTE → CRAFT → [FLOW](FLOW.md) → trang này →
bốn SKILL.md dưới đây. Reference, pattern và nền tảng chỉ mở đúng phần cần khi quyết định phát sinh.
Không đọc cả craft standards, PATTERNS hay thư viện pattern như điều kiện khởi đầu.
Website hoặc landing: đọc thêm [`owner-picks.md`](foundations/owner-picks.md) mục 5–6 (hỏi chủ repo về ảnh và
trang mẫu trước khi dựng) và lấy chuyển động từ [`motion-recipes`](foundations/motion-recipes/index.html).
Đo cùng đơn vị tách whitespace bằng `python scripts/reading-paths.py`; số trước/sau kèm file thực đọc.


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
6. **Dựng và phản biện** theo rubric, sửa, dựng lại.
   Với luồng có dữ liệu, bấm thử từ chọn/nhập → xác nhận → quay lại sửa → xác nhận lại. Đối chiếu
   cùng dữ liệu trên mọi màn (số lượng, biến thể, tổng tiền, ngày giờ); kiểm tra giữ lựa chọn và
   ít nhất một nhánh lỗi/khôi phục. Ghi kết quả riêng với soát giao diện; `taste-check` không
   chứng minh luồng đúng.
7. **Bàn giao**: đặc tả trạng thái, token, hành vi tương tác.

- Skill: [`ux-structure-and-flow-design`](skills_UIUX/ux-structure-and-flow-design/SKILL.md) ·
  [`visual-design-direction`](skills_UIUX/visual-design-direction/SKILL.md) ·
  [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md) ·
  [`design-critique-and-rationale`](skills_UIUX/design-critique-and-rationale/SKILL.md)
- Bắt buộc: [`CRAFT.md`](CRAFT.md) và khối kế hoạch thị giác của nó trước bước 5. Cần chi tiết hơn
  thì mở [craft standards](skills_UIUX/ui-craft-and-visual-qa/references/craft-standards.md).
- Mobile thêm: [`mobile-app-design`](skills_UIUX/mobile-app-design/SKILL.md) + spec sheet nền tảng (mục 3).
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

Như **M**, cộng thêm:

1. **Đánh giá hiện trạng** và so 3–5 sản phẩm tham chiếu (trích nguyên tắc, không sao chép bề mặt).
   Thiếu hiểu biết về người dùng thì thêm [`research-lite`](skills_UIUX/research-lite/SKILL.md).
2. **Kiến trúc thông tin** và mô hình điều hướng cho toàn khu vực.
3. **Hướng thị giác**: 4–7 thuộc tính thị giác có biểu hiện cụ thể, ma trận vai trò trang, màn hình.
   Nền tảng lý do nằm trong [`foundations/`](foundations/README.md).
   Hướng chỉ được nhân rộng sau [cổng duyệt hướng](#cổng-duyệt-hướng-m-l-xl).
4. **Thử trên 3 màn hình khác bản chất** trước khi nhân rộng.
5. **Critique 3 vòng** (xem rubric): tự review → review chéo theo vai trò → review "người lạ" chỉ nhìn ảnh.
6. Kiểm nhất quán xuyên màn hình (ảnh đặt cạnh nhau).

- Sản phẩm đã có code: [`brownfield-redesign`](skills_UIUX/brownfield-redesign/SKILL.md) là bắt buộc;
  bước "đánh giá hiện trạng" ở trên gồm cả kiểm kê code cũ và bảng ADN của skill đó.
- Skill thêm: [`website-audit-and-redesign`](skills_UIUX/website-audit-and-redesign/SKILL.md) hoặc
  [`mobile-app-design`](skills_UIUX/mobile-app-design/SKILL.md) ·
  [`design-reference-research-and-benchmark`](skills_UIUX/design-reference-research-and-benchmark/SKILL.md) ·
  [`information-architecture`](skills_UIUX/information-architecture/SKILL.md)
- Giao: tất cả của M, cộng bản đánh giá hiện trạng, hướng thị giác, ma trận màn hình, ảnh nhất quán xuyên màn hình.
- Ngưỡng: trung bình ≥ 4, không chiều nào < 3.5, không hard-fail.

### XL — Sản phẩm mới / chưa có design system

Như **L**, cộng thêm:

1. **Khám phá**: vấn đề, đối tượng, giả định rủi ro nhất, cách kiểm chứng, theo
   [`design-thinking-lite`](skills_UIUX/design-thinking-lite/SKILL.md) mức XL và
   [`research-lite`](skills_UIUX/research-lite/SKILL.md).
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
| **Cải thiện UI đang có** | Sửa và trau chuốt (Polish), giữ bố cục và hành vi | Chọn XS–S theo bảng cỡ việc, dùng [`ui-craft-and-visual-qa`](skills_UIUX/ui-craft-and-visual-qa/SKILL.md#cải-thiện-giao-diện-hiện-có); sửa ở token và CSS component đang có, không thêm lớp đè |
| **Redesign sản phẩm có code** | Thiết kế lại, làm mới, nâng cấp một sản phẩm đã có code chạy được | L (hoặc M nếu một khu vực nhỏ) + [`brownfield-redesign`](skills_UIUX/brownfield-redesign/SKILL.md): kiểm kê code cũ, ghi ADN, lưới test hành vi, thay tại nguồn và xoá code bị thay, soát bằng `overlay-check.py`. Website cần audit IA, SEO thì thêm `website-audit-and-redesign` |
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
  không còn lỗi ở cả 390 px và 1280 px (website thêm 768 và 1440). Không chạy được thì chạy
  `static-check.cjs`, soát bằng mắt theo [README công cụ QA](skills_UIUX/ui-craft-and-visual-qa/scripts/README.md)
  và ghi rõ. Màn desktop
  và artboard canvas đạt thêm `--layout strict` (không còn màn trống, nội dung dồn một bên, card mỏng).
- Đã **nhìn ảnh chụp trang đã dựng**, không chỉ đọc code.
- Đủ trạng thái liên quan (rỗng, đang tải, lỗi, nội dung dài, chữ lớn, tối).
- Kiểm luồng riêng theo [FLOW.md](FLOW.md): CTA đúng đích/đối tượng/vai trò, Back giữ ngữ cảnh,
  sửa → kiểm tra hậu quả phù hợp → kết quả, dữ liệu/tổng tiền khớp, lỗi có khôi phục.
  `flow-check` không có lỗi chắc chắn; cảnh báo được xét từng trường hợp. Luồng bắt buộc FAIL hoặc UNKNOWN
  chặn kết luận Đạt dù render/rubric tốt. Demo ghi rõ phần mô phỏng và phạm vi gallery.
- Contrast và vùng chạm đạt chuẩn trong [`CRAFT.md`](CRAFT.md); không chạm mặc định nào trong danh sách
  cấm mà không có lý do từ brief.
- Rubric đạt ngưỡng của cỡ việc, không hard-fail.
- Ghi rõ điều gì **chưa** kiểm chứng (người dùng thật, thiết bị thật, trình đọc màn hình).
- M trở lên: hướng thị giác đã qua cổng duyệt, hoặc ghi `CHƯA DUYỆT`. L và XL có duyệt độc lập theo
  [hồ sơ ảnh](skills_UIUX/design-critique-and-rationale/references/independent-review.md).
- Lỗi mới mà checker và rubric đều không bắt được thì ghi một dòng vào [`TASTE-LOG.md`](TASTE-LOG.md).
- Redesign sản phẩm có code: `overlay-check.py` không còn lỗi, test hành vi xanh trước và sau, ADN được
  giữ hoặc người quyết định đã chọn bỏ (xem [`brownfield-redesign`](skills_UIUX/brownfield-redesign/SKILL.md)).
