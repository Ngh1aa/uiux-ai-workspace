---
name: website-audit-and-redesign
description: |
  Audit website hiện có trước khi redesign/rebuild. Dùng khi có live URL, legacy code, sitemap cũ
  hoặc yêu cầu “làm lại website”; bảo toàn content/SEO/flow tốt, xác định friction, technical/design debt,
  owner-user mismatch và redesign scope trước khi thay đổi UI/code.
---

# Website Audit & Redesign

## Goal

Redesign không đồng nghĩa xóa và làm lại. Phải biết:

`giữ gì → sửa gì → bỏ/gộp gì → thêm gì → và quan trọng: cái gì phải thay đổi đủ rõ để redesign có lý do tồn tại`

Audit phải tạo được **Redesign Contract**, không chỉ danh sách issue.

## 1. Prerequisites

Có ít nhất một trong: live URL, source code, sitemap, analytics, screenshots, stakeholder brief.

Nếu thiếu business brief, route `product-discovery`. Nếu có source + live site, inspect cả hai; source không thay rendered evidence.

## 2. Inventory

| Page/template | Purpose | Primary user | Entry context | Primary CTA | Content/SEO value | Decision |
|---|---|---|---|---|---|---|

Decision: `KEEP | IMPROVE | MERGE | REMOVE | ADD`.

Thu thập navigation, URLs, forms, search/filter, media, downloads, schema, redirects, integrations và shared layout/components.

## 3. Owner goal ↔ user goal audit

Với whole-site redesign, bắt buộc tạo:

| Owner wants to show/prove | User wants to know/do | Intersection | Website responsibility | Proof needed | CTA timing |
|---|---|---|---|---|---|

Nếu current site ưu tiên owner message nhưng user không tìm được decision evidence, ghi rõ mismatch.

## 4. Journey / entry audit

Không mặc định homepage là entry point.

Với primary journeys kiểm:

- organic/deep page entry có tự định hướng được không;
- user biết mình đang ở đâu và next step không;
- evidence xuất hiện trước CTA chưa;
- path có dead-end/loop/duplicate không;
- mobile có friction khác desktop không;
- conversion commitment có đúng system reality không.

## 5. Page-family audit — bắt buộc

Nhóm page theo role, không chỉ theo URL:

- overview/brand;
- category/hub;
- product/spec/detail;
- evidence/trust;
- experience/amenities;
- search/availability/listing;
- conversion/contact;
- utility/content.

Với mỗi family ghi:

| Page family | User question | Existing composition | What works | Template smell | Redesign implication |
|---|---|---|---|---|---|

### Template monotony smell

Flag P1 nếu nhiều materially different page roles đều dùng cùng:

- hero shell chỉ thay ảnh/chữ;
- `heading + 3 cards`;
- copy-left/image-right;
- same section rhythm;
- same CTA placement;

mà không có brand/task rationale.

## 6. Visual/brand audit

Audit từ macro đến micro:

1. visual hierarchy;
2. page-family composition;
3. layout/grid/rhythm;
4. brand recognition without logo;
5. color roles + logo/CTA contrast states;
6. typography;
7. media/art direction;
8. components/states;
9. responsive transformation.

Không viết “xấu/cũ”. Mỗi material finding dùng:

`evidence → user/business impact → root cause → redesign implication`.

## 7. Technical/design debt audit

Ngoài SEO/technical, kiểm design implementation debt:

- CSS override layers chồng nhau;
- page-local patch cho shared defect;
- duplicate tokens/components;
- legacy generator/source owner không còn đúng;
- cached/versioned assets làm redesign không hiện;
- responsive behavior phân tán;
- fake dynamic states/inventory/success.

Mục tiêu là biết **owner nào phải thay**, không chỉ selector nào cần patch.

## 8. SEO/URL preservation

Trước khi đổi IA/slug:

- record current URLs + intent;
- identify organic/backlink/internal-link value;
- preserve hoặc create redirect strategy;
- check metadata/canonical/robots/sitemap/schema/status;
- không xóa content có value chỉ vì layout cũ.

## 9. Preserve list

Bắt buộc ghi rõ:

- content/feature tốt;
- brand assets/equity;
- SEO/URL equity;
- useful navigation conventions;
- successful conversion paths;
- useful components/tokens;
- verified business facts.

## 10. Visible Redesign Delta — bắt buộc

Một redesign phải định nghĩa trước **người xem sẽ nhận ra điều gì khác**.

Tạo:

| Current visible problem | Why it matters | New design behavior | Expected visible delta | Verification |
|---|---|---|---|---|

Ví dụ delta có thể nằm ở:

- hierarchy/composition;
- page-role diversity;
- brand signature;
- navigation/orientation;
- decision objects;
- content proof placement;
- media direction;
- mobile composition.

Không dùng “modern hơn / premium hơn” làm delta.

### Redesign recognizability gate

Nếu stakeholder mở before/after ở cùng viewport mà khó nhận ra thay đổi ngoài màu/font/spacing nhỏ, trong khi request là substantial redesign, scope/design direction đang sai hoặc implementation chưa đủ.

Ngược lại, novelty lớn nhưng phá brand/journey/SEO cũng fail.

## 11. Priority matrix

| Finding | Evidence | User impact | Business impact | Root owner | Effort | Risk | Priority | Decision |
|---|---|---|---|---|---|---|---|---|

Ưu tiên: broken critical journey/system reality → owner-user mismatch → page hierarchy/IA → mobile/accessibility → brand/composition → craft.

## 12. Output

Tạo `docs/website-audit.md` gồm:

1. site/template inventory;
2. owner-user intersection;
3. journey/entry findings;
4. page-family audit;
5. visual/brand audit;
6. technical/design debt;
7. preserve list;
8. SEO/URL risks;
9. priority matrix;
10. **Visible Redesign Delta**;
11. redesign scope/handoff to reference research + visual direction.

## Acceptance criteria

- [ ] Audit đủ primary page families/journeys, không chỉ homepage.
- [ ] Owner goal ↔ user goal đã map.
- [ ] Mỗi material finding có evidence + impact + root owner/action.
- [ ] Có Keep/Improve/Merge/Remove/Add.
- [ ] Có preserve list.
- [ ] Có template-monotony/page-family audit.
- [ ] Có design/technical debt owner audit, không chỉ symptoms.
- [ ] Có SEO/URL migration risk.
- [ ] Có Visible Redesign Delta đủ cụ thể để verify.
- [ ] Redesign scope trace được về business/user/brand, không chỉ aesthetics.

## Anti-patterns

- Redesign chỉ vì “style cũ”.
- Chỉ audit homepage.
- Copy competitor mà không hiểu task/context.
- Xóa URL/content trước migration plan.
- Đánh đồng novelty với UX improvement.
- Audit 50 lỗi micro nhưng bỏ qua page-family monotony/hierarchy.
- Định nghĩa redesign bằng palette/font/effect mà không có visible composition/journey delta.
