# Danh mục skill

Danh mục để tra cứu, **không phải** để chọn quy trình. Chọn skill theo cỡ việc trong
[`WORKFLOWS.md`](../WORKFLOWS.md), bắt đầu từ [`START-HERE.md`](../START-HERE.md). Có 29 skill; mỗi skill
là một thư mục có `SKILL.md`. Cột "Dùng khi" nói lúc nào mở; cột "Không dùng khi" chỉ sang skill đúng hơn.

## Thương hiệu và hướng thị giác

| Skill | Dùng khi | Không dùng khi |
|---|---|---|
| `brand-guidelines` | Tiếp nhận thương hiệu khách (mức A–D) và áp vào token; đi cùng `BRAND-BRIEF.template.md` | Thương hiệu đã có, cần dấu ấn riêng trên màn: `brand-distinctiveness-and-visual-signature` |
| `brand-distinctiveness-and-visual-signature` | Biến nhận diện thành dấu hiệu lặp lại trên các màn; tìm vật gốc của ngành | Chưa có thương hiệu: `brand-guidelines` trước |
| `visual-design-direction` | Chốt chữ, màu, hình khối, bố cục cho dự án; soát độ riêng, chống "nhìn như template" | Chỉ sửa một màn đã có hướng: `ui-craft-and-visual-qa` |
| `experience-principles-and-signature-moments` | Cỡ XL: 3–5 nguyên tắc trải nghiệm có đánh đổi, chọn khoảnh khắc đáng nhớ | Việc M trở xuống |
| `design-reference-research-and-benchmark` | Tìm và chấm tham khảo theo ngành, rút nguyên tắc, không chép | Dựng lại đúng theo Figma hay ảnh: `frontend-implementation` |
| `asset-media-and-art-direction` | Chọn ảnh, minh hoạ, icon, video; ảnh bị cắt sai, vỡ tỉ lệ | Thứ tự nguồn ảnh và bộ icon: [ảnh và icon](../foundations/images-and-icons.md) đủ |
| `motion-and-microinteractions` | Chuyển động có mục đích, thời lượng, giảm chuyển động | Chuyển động theo cuộn cho website: [motion](../foundations/motion.md) |

## Vấn đề, người dùng, cấu trúc

| Skill | Dùng khi | Không dùng khi |
|---|---|---|
| `design-thinking-lite` | Brief chỉ nêu giải pháp, chưa rõ vấn đề; cần câu "Làm sao để" và 3+ hướng; nghiên cứu gọn kèm nhãn mức bằng chứng | Vấn đề và người dùng đã rõ: vào thẳng `ux-structure-and-flow-design` |
| `audience-intent-and-top-tasks` | Website: ai vào, từ đâu, cần làm gì trước | App đã biết việc chính |
| `ux-structure-and-flow-design` | Việc chính, luồng, kiểm kê màn × trạng thái, wireframe trước khi tô màu | Chỉ một component: `state-feedback-and-error-recovery` |
| `information-architecture` | Điều hướng, nhãn, sơ đồ trang; tìm kiếm và bộ lọc toàn site | Lọc trong một bảng: `data-tables-and-enterprise-ux` |
| `website-audit-and-redesign` | Website cũ cần audit IA, nội dung, SEO trước khi làm lại | Sản phẩm có code cần thay giao diện: `brownfield-redesign` |
| `brownfield-redesign` | Thiết kế lại sản phẩm đã có code: kiểm kê, giữ ADN, test hành vi, thay tại nguồn; có `overlay-check.py` | Chỉ trau chuốt, giữ bố cục: `ui-craft-and-visual-qa` |

## Nội dung và chữ

| Skill | Dùng khi | Không dùng khi |
|---|---|---|
| `ux-writing-and-microcopy` | Nhãn nút, lỗi, trạng thái rỗng, thông báo; cấu trúc nội dung và câu hỏi trong form | Lập luận cả trang marketing: `conversion-and-content` |
| `conversion-and-content` | Trang marketing: lập luận, bằng chứng, CTA; uy tín, minh bạch; soát mẫu lừa người dùng | Chữ trong app: `ux-writing-and-microcopy` |
| `localization-and-i18n` | Nhiều ngôn ngữ, định dạng ngày, tiền, chữ dài ra khi dịch | Chỉ tiếng Việt |

## Thành phần, trạng thái, tương tác

| Skill | Dùng khi | Không dùng khi |
|---|---|---|
| `design-system-and-components` | Token, component, biến thể; dựng hoặc mở rộng hệ thống | Dùng component có sẵn: `design-system/` đủ |
| `interaction-patterns-and-form-ux` | Form dài, wizard, tab, dialog, tìm và lọc trong màn; đăng nhập, đăng ký, khôi phục tài khoản | Chỉ chữ trong form: `ux-writing-and-microcopy` |
| `state-feedback-and-error-recovery` | Đủ trạng thái: tải, rỗng, lỗi, khôi phục, nội dung dài | Cả luồng nhiều màn: `ux-structure-and-flow-design` |
| `data-tables-and-enterprise-ux` | Bảng dữ liệu dày, chọn nhiều, thao tác hàng loạt | Biểu đồ, KPI: `data-visualization-and-dashboard-ux` |
| `data-visualization-and-dashboard-ux` | Dashboard, biểu đồ, chọn loại biểu đồ, panel cân lưới | Bảng: `data-tables-and-enterprise-ux` |
| `human-ai-interaction-design` | Tính năng có AI tạo nội dung hay ra quyết định | AI chỉ là công cụ làm thiết kế |
| `accessibility` | WCAG 2.2 AA, bàn phím, focus, trình đọc màn hình, khả năng nhận thức | Chỉ cần tương phản và vùng chạm: `CRAFT.md` đủ |

## Nền tảng

| Skill | Dùng khi | Không dùng khi |
|---|---|---|
| `mobile-app-design` | Mọi việc thiết kế app; quy ước iOS và Android là hướng dẫn con bên trong | Website trên điện thoại: `responsive-and-device-strategy` |
| `responsive-and-device-strategy` | Website: breakpoint, bố cục theo cỡ màn | App native: `mobile-app-design` |
| `industry-playbooks` | Đã biết ngành của khách: 13 playbook | Ngành không có playbook: bỏ qua |

## Dựng, soát, phê bình

| Skill | Dùng khi | Không dùng khi |
|---|---|---|
| `frontend-implementation` | Dựng HTML/CSS đúng ngữ nghĩa; dựng lại theo Figma hay ảnh; tốc độ tải, Core Web Vitals | Chỉ soát giao diện đã dựng: `ui-craft-and-visual-qa` |
| `ui-craft-and-visual-qa` | Cải thiện UI hiện có, soát prototype; có `taste-check.cjs`, `static-check.cjs`, `flow-check.cjs` | Đổi hướng thiết kế: `visual-design-direction` |
| `design-critique-and-rationale` | Phê bình theo rubric và heuristic, ghi lý do thiết kế, review độc lập | Sửa lỗi cụ thể đã biết: `ui-craft-and-visual-qa` |

## Skill đã gộp

Các tên dưới đây không còn là skill riêng; nội dung giữ nguyên trong hướng dẫn con của skill chủ.
Gặp tên cũ trong tài liệu thì mở skill chủ. Danh sách máy đọc: [`merged-skills.json`](merged-skills.json).

| Skill chủ | Hướng dẫn con |
|---|---|
| `visual-design-direction` | visual-taste-calibration |
| `brand-distinctiveness-and-visual-signature` | real-world-artifact-and-domain-metaphor-design, brand-recognition-and-consistency-qa |
| `design-thinking-lite` | research-lite |
| `mobile-app-design` | ios-app-design, android-app-design, mobile-navigation-and-state-ux, mobile-design-system-and-handoff, mobile-prototype-and-qa, mobile-web-preview |
| `ux-writing-and-microcopy` | content-design-and-question-design |
| `conversion-and-content` | trust-credibility-and-transparency, ethical-ux-and-deceptive-patterns |
| `information-architecture` | site-search-and-findability |
| `interaction-patterns-and-form-ux` | authentication-account-and-recovery-ux, complex-forms-and-wizards, complex-workflow-and-progress-ux |
| `asset-media-and-art-direction` | media-crop-and-layout-integrity |
| `frontend-implementation` | reference-analysis-and-design-to-code, web-quality-and-performance |
| `design-critique-and-rationale` | ux-laws-and-heuristics |
| `ui-craft-and-visual-qa` | visual-redesign-delta-gate, visual-regression-and-design-drift; `ui-improvement` → [cải thiện UI](ui-craft-and-visual-qa/SKILL.md#cải-thiện-giao-diện-hiện-có), `prototype-visual-experience-qa` → [soát prototype](ui-craft-and-visual-qa/SKILL.md#soát-prototype) |
| `audience-intent-and-top-tasks` | entry-context-and-visit-intent, journey-driven-content-and-layout |
| `accessibility` | inclusive-design-and-cognitive-accessibility |

## Đã gỡ khỏi `main`

Các skill nghiên cứu người dùng đầy đủ, chiến lược sản phẩm, đo lường sau ra mắt, SEO, vận hành,
kiểm thử code, quản trị thư viện và bộ chạy tự động cũ (flows, profiles, prompts, vendor) đã được
gỡ vì không dùng khi thiết kế qua chat. Bản đầy đủ ở nhánh `archive/truoc-khi-gon-lan-2`. Nếu một
skill còn nhắc tên một skill đã gỡ (ví dụ "dùng `seo-strategy` cho việc đó"), hiểu đó là việc
nằm ngoài phạm vi repo, không đi tìm skill đó. Phần nghiên cứu cần cho thiết kế qua chat nằm gọn trong
hướng dẫn con `research-lite` của `design-thinking-lite`.
