---
name: visual-redesign-delta-gate
description: |
  Hard gate cho substantial redesign để chặn failure mode "code thay nhiều nhưng website nhìn vẫn như cũ".
  Bắt buộc so before/after cùng viewport, kiểm silhouette/composition/page-role diversity và FAIL nếu thay đổi
  chủ yếu chỉ là màu, font, spacing, radius, shadow hoặc decorative effects.
---

# Visual Redesign Delta Gate

## Goal

Redesign phải tạo ra thay đổi **nhìn thấy được ở cấu trúc trải nghiệm**, không chỉ thay skin.

`current rendered UI → redesign intent → composition proof → implemented render → old-vs-new comparison → PASS/FAIL`

Skill này là hard gate cho whole-site/substantial redesign và phải được route ở cả 3 giai đoạn:

1. Prompt 1 / pre-design research: định nghĩa delta trước khi code.
2. Prompt 2 / implementation: chứng minh delta trên representative pages trước rollout.
3. Prompt 3 / final QA: verify old-vs-new sau implementation, không chỉ new-vs-contract.

## 1. Trigger

Bật khi user dùng các intent như:

- redesign / rebuild / làm lại toàn bộ giao diện;
- nâng cấp toàn bộ website;
- website nhìn cũ/generic/template;
- "khác hẳn", "wow hơn", "đổi toàn bộ UI/UX";
- user phản hồi rằng bản mới chỉ đổi màu/font nhưng bố cục vẫn như cũ.

Không dùng hard gate này cho một micro-fix/local component tweak.

## 2. Capture current-state baseline BEFORE design

Với existing UI, trước khi khóa direction phải có rendered baseline nếu tooling cho phép.

Tối thiểu:

- 3–6 primary page roles;
- desktop + mobile cho representative pages;
- top-of-page và ít nhất một full-page/long-page capture khi relevant;
- key interaction/state nếu nó materially ảnh hưởng composition.

Record:

| Route/role | Viewport | Current silhouette | First visual anchor | Section rhythm | Main decision object | Template smell |
|---|---:|---|---|---|---|---|

Source/code inspection không thay baseline screenshot.

## 3. Define a Redesign Delta Contract BEFORE code

Tạo artifact:

| Page role | Current recognizable structure | New intended structure | What must visibly disappear/change | New visual anchor | Mobile transformation | Verification |
|---|---|---|---|---|---|---|

Mỗi primary page role phải có ít nhất một **structural delta** thuộc các nhóm:

- first visual anchor / top composition;
- grid/silhouette;
- information hierarchy;
- media-to-copy relationship;
- decision object placement;
- navigation/orientation behavior;
- section sequence/rhythm;
- mobile composition;
- interaction model materially visible to users.

Color/font/spacing/radius/shadow/motion polish **không được tính là structural delta** nếu đứng một mình.

## 4. Silhouette test — HARD FAIL

Tạo old/new screenshot ở cùng route + viewport.

Sau đó mentally hoặc bằng image-processing abstraction:

- bỏ text content;
- bỏ logo/brand name;
- giảm ảnh thành các khối grayscale/blur;
- bỏ màu brand.

Hỏi:

> Nếu chỉ nhìn silhouette, khối media, hierarchy và rhythm, old và new có còn gần như cùng một layout không?

Nếu CÓ với substantial redesign → **FAIL**.

### Examples of FAIL

- hero copy-left/image-right giữ nguyên, chỉ đổi nền trắng;
- vẫn `heading → 3 cards → banner → 3 cards`, chỉ đổi typography;
- cùng grid/crop/CTA positions, chỉ thêm glass/gradient;
- cùng mobile stack, chỉ tăng khoảng trắng;
- cùng universal hero trên mọi page, chỉ đổi ảnh/title.

## 5. Composition-change budget

Không yêu cầu novelty ngẫu nhiên, nhưng substantial redesign phải chứng minh đủ delta.

Mặc định cho site có 5+ materially different primary roles:

- ≥3 distinct top-of-page composition families;
- representative set có ≥3 materially different page silhouettes;
- ít nhất 2 primary roles phải thay structural hierarchy so với current baseline;
- mobile phải có ít nhất một intentional re-composition, không chỉ stack desktop;
- shared design system có thể nhất quán, nhưng page-role composition không được đồng nhất vì code convenience.

Nếu project rationale yêu cầu repetition mạnh, document reason + user/business benefit.

## 6. Reference-transfer gate

Khi research reference:

- production/category sites dùng cho IA/task/conversion;
- award/editorial sites dùng cho composition/type/media/motion;
- không clone một site;
- mỗi reference phải có role cụ thể;
- extracted principle phải dẫn đến delta cụ thể trong project.

Nếu benchmark tạo ra moodboard đẹp nhưng Redesign Delta Contract vẫn giống current layout → benchmark FAIL.

## 7. Representative-page implementation gate

Prompt 2 phải implement 2–4 representative page roles trước.

Render old/new cùng viewport và tạo contact sheet.

PASS chỉ khi:

- first impression khác rõ ở hierarchy/composition;
- page roles không thể hoán đổi copy/image cho nhau;
- visual signature tồn tại khi che logo;
- preserve list/SEO/behavior không bị phá;
- mobile không phải desktop co lại;
- delta phục vụ owner ↔ user goal, không phải novelty trang trí.

Nếu FAIL → không rollout toàn site. Quay lại composition owner.

## 8. Final QA old-vs-new gate

Prompt 3 không được chỉ hỏi "new có đẹp/đúng contract không?".

Phải review 3 lớp:

1. **OLD vs NEW** — redesign delta có thật không?
2. **NEW vs DESIGN CONTRACT** — implementation có đúng direction không?
3. **NEW CROSS-PAGE** — có template monotony/brand drift không?

Tạo matrix:

| Route | Old evidence | New evidence | Structural delta | Cosmetic-only risk | Result |
|---|---|---|---|---|---|

Substantial redesign FAIL nếu majority representative routes chỉ thay cosmetic layers.

## 9. User-feedback regression rule

Nếu user nói một trong các câu kiểu:

- "website vẫn y như cũ";
- "chỉ đổi nền trắng chữ đen";
- "xài 3 prompt mà vẫn không khác";

thì coi đây là **process regression**, không phải subjective preference đơn thuần.

Bắt buộc:

1. compare current implementation với baseline;
2. identify gate nào đã PASS sai;
3. sửa root design/composition owner;
4. thêm regression assertion vào prompt/skill/eval;
5. re-run old-vs-new screenshot gate trước release.

## 10. Release gate

Không release substantial redesign khi chưa có:

- baseline old screenshots hoặc documented reason vì sao không capture được;
- new rendered screenshots;
- old-vs-new contact sheet;
- representative page-role diversity check;
- mobile delta check;
- no P0/P1 visual blocker;
- deployment source verified;
- post-deploy smoke trên production URL.

Nếu render evidence không có: `REDESIGN DELTA: UNVERIFIED/BLOCKED`.

## 11. Completion language

Không nói:

- redesigned;
- visually finished;
- substantially upgraded;
- whole-site redesign complete;

nếu chỉ có source diff/build success hoặc cosmetic changes.

## Acceptance checklist

- [ ] Old rendered baseline exists for representative routes.
- [ ] Redesign Delta Contract defines structural changes per role.
- [ ] At least 3 composition families exist when scope warrants it.
- [ ] Old/new same-viewport screenshots were compared.
- [ ] Silhouette test passes.
- [ ] Representative pages pass before rollout.
- [ ] Cross-page contact sheet shows role diversity.
- [ ] Mobile has intentional re-composition.
- [ ] Final QA reviews old-vs-new, not only new-vs-contract.
- [ ] User feedback about "looks the same" becomes regression coverage.

## Core principle

> **A redesign is not measured by lines changed. It is measured by whether the information hierarchy, composition, journey and brand expression are visibly and usefully different while preserving what should remain.**
