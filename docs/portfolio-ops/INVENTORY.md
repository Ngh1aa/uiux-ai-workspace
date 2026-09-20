# INVENTORY.md — Night 0

Cập nhật: 2026-09-21

## Evidence baseline

- **VERIFIED:** `AGENTS.md` yêu cầu source-of-truth, evidence states, root-cause repair và không gọi DONE khi chưa verify.
- **VERIFIED:** `README.md` xác nhận `uiux-factory/` là canonical runtime; standalone `showcase/` đã bị removed. Vì vậy implementation phải diễn ra ở target repositories, còn repo này là control plane.
- **VERIFIED:** portfolio `portfolio-grouping.js` hiện nhóm 12 project theo E-commerce, Fintech, B2B, AI, Mobility, EdTech; `index.html` còn có Lumen như active project.
- **VERIFIED:** có hai Draft PR cũ #30 và #31 từ workflow trước; không sửa/merge chúng trong P0 mới.
- **UNKNOWN:** rendered QA, accessibility, design-system completeness và research depth của từng target project chưa được audit trực tiếp trong run P0 này. Theo contract, UNKNOWN không được nâng thành PASS.

## Tier proposal — INFERRED, chờ OWNER review

### Tier A — flagship
1. **Lumen** — digital cultural experience; mạnh về visual/interaction craft, khác domain với các dashboard.
2. **Nova** — consumer fintech; chứng minh trust-heavy product flows và mobile/product thinking.
3. **Sentry** — fraud/risk operations; data-heavy, high-stakes decision UX.
4. **LuxRoom** — high-consideration commerce; image-led product confidence và ecommerce depth.
5. **Access** — enterprise identity/permissions; B2B SaaS + complex governance IA.

Lý do: nhóm này phủ cultural/editorial, consumer fintech, operations/data-heavy, commerce và enterprise thay vì để flagship lệch một domain.

### Tier B — supporting
- Atelier — luxury/editorial commerce.
- Flux — B2B fintech/treasury.
- CENNEXT — B2B/industrial service experience.
- VAS Education — EdTech/institutional journeys.

### Tier C — Explorations / portfolio breadth
- Violet Marketplace.
- Capital Place.
- VOLTIS.
- UIUX Factory được giữ như **system/tooling proof**, không chấm như một product case ngang flagship.

## Rủi ro cần audit ở các bước sau
- License/attribution của imagery và external component inspiration: UNKNOWN cho từng project.
- Một số repo mapping chưa được portfolio source khai báo trực tiếp: UNKNOWN.
- Các claim case study hiện hữu phải được kiểm tra để không biến heuristic/concept thành user-research evidence.
- Light/dark chỉ là depth-floor bắt buộc khi product scope hỗ trợ theme; không ép theme giả vào project editorial chỉ để đủ checklist.

## Inspiration policy
Nguồn được phép theo workflow: 21st.dev, Flux UI, Animata, Kyla Prompt, HuggingPT UI Prompts, Bmob Prompt, UIAI. P0 **không dùng code/component** từ các nguồn này, vì vậy không phát sinh third-party license entry. Khi vào project, tối đa 2–3 nguồn/domain và dùng ADOPT/ADAPT/REJECT; UNKNOWN license = inspiration only.
