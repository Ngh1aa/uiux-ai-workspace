---
name: visual-design-direction
description: |
  Chuyển brand, IA và reference intelligence thành visual direction cụ thể cho website: layout grammar,
  hierarchy, typography, color roles, imagery, depth và motion principles. Dùng trước design system/code
  hoặc khi UI hiện tại generic, thiếu nhịp điệu, không phản ánh brand/domain.
---

# Visual Design Direction

## Goal

Tạo một **visual grammar có lý do**, không phải moodboard adjective (“modern, clean, premium”) rồi code tùy hứng.

## Inputs

- Brand identity/constraints.
- Domain expectations và audience trust needs.
- Page templates/IA.
- Content/image reality.
- Existing design strengths cần preserve.
- `docs/design-reference-benchmark.md` khi substantial redesign/new visual direction đã chạy reference research.
- `docs/real-world-artifact-design.md` khi domain-native objects/documents/rituals đã được research và có transfer potential.

Nếu scope đủ lớn nhưng visual direction còn generic và chưa có reference benchmark, route sang `design-reference-research-and-benchmark` trước khi khóa system.

Nếu domain có physical/printed/spatial/service artifacts mạnh và visual direction vẫn generic/card-heavy hoặc thiếu ownable domain DNA, route sang `real-world-artifact-and-domain-metaphor-design` trước khi khóa grammar.

## Workflow

1. Audit reference benchmark theo *principle*, không copy surface; nếu chưa có benchmark và task cần reference intelligence, tạo nó trước.
2. Khi applicable, audit domain-artifact research theo *mental model + transferable property*, không literal imitation; ưu tiên lowest useful metaphor fidelity.
3. Synthesize digital references + domain artifacts + brand truth thành một design DNA coherent; không Frankenstein nhiều style/metaphor.
4. Define 4–7 visual attributes kèm biểu hiện cụ thể.
5. Define layout grammar: container, grid, asymmetry/symmetry, section rhythm, density.
6. Define hierarchy: display/H1/H2/body/meta/action.
7. Define color role map, không chỉ palette.
8. Define typography pairing/scale/line-length strategy.
9. Define image/illustration/icon art direction.
10. Define elevation/border/radius language theo brand, không theo trend mặc định.
11. Define motion purpose/intensity và reduced-motion behavior.
12. Define a **page-role composition matrix** before coding.
13. Stress-test trên ít nhất 3 materially different page types + mobile trước khi khóa system.

## Mandatory page-role composition matrix

Với mỗi primary page/template, ghi rõ:

`page role → user question on entry → owner message → first visual anchor → top-of-page composition → decision object → primary CTA → media treatment → mobile transformation`

Ví dụ page roles có thể là `brand/overview`, `location`, `product/specification`, `evidence/ESG`, `amenities/experience`, `availability/search`, `contact/conversion`. Tên cụ thể phụ thuộc domain.

### Top-of-page / hero diversity gate

- Hero/top-of-page **không phải component để copy rồi thay title + image** trên mọi trang.
- Hai page có user task khác nhau phải được kiểm xem có cần first visual anchor khác nhau không: map, floor plan, evidence, product object, editorial image, data, form, timeline, comparison, etc.
- Với site có 5+ materially different primary page roles, mặc định cần ít nhất **3 composition families** ở top-of-page, trừ khi brand/product rationale ghi rõ vì sao repetition mạnh là đúng.
- Reuse navigation, tokens, typography, signature motif và interaction language để tạo consistency; không reuse một shell duy nhất để tạo monotony.
- Nếu 3 screenshot đầu trang có thể hoán đổi copy/image cho nhau mà vẫn “đúng”, direction chưa đủ page-specific và **chưa được code**.
- Utility pages có thể dùng family chung khi user intent tương tự; primary decision pages không được đồng nhất chỉ để code nhanh.

## Business ↔ user ↔ visual mapping gate

Trước code phải trả lời được cho mỗi primary page:

1. Chủ website muốn chứng minh/show điều gì?
2. Người dùng vào trang này muốn biết/ra quyết định gì trước?
3. Content nào là evidence/decision object mạnh nhất?
4. Composition nào giúp hai mục tiêu đó gặp nhau nhanh nhất?

Nếu visual choice không trace được về ít nhất một trong các câu hỏi trên, coi đó là decoration và loại bỏ hoặc hạ vai trò.

## Brand evidence rules

- Brand guideline chính thức > first-party website/brand assets > verified logo/identity evidence > inference.
- Nếu không có brand guideline, có thể derive **limited working roles** từ logo, official site, imagery và existing assets nhưng phải đánh dấu phần nào là evidence, phần nào là inference.
- Không suy ra cả một luxury/minimal/glass/gradient style chỉ từ một màu logo.
- Brand color phải có role cụ thể như CTA, wayfinding, evidence emphasis, section field, state hoặc navigation datum; không rải màu để “trông branded”.

## Reference synthesis rules

- Mỗi reference cần có job rõ: IA, layout, type, imagery, motion, conversion hoặc mobile.
- Real production site có trọng lượng cao hơn gallery shot cho UX/task decisions.
- Award/curated reference có thể mạnh về craft nhưng không tự động chứng minh usability, accessibility, performance hay conversion.
- Không lấy nguyên “look” của một site; extract pattern rồi map về brand/content/assets hiện có.
- Nếu reference đòi asset/3D/video mà project không có, adapt grammar thay vì giả lập bằng filler.
- Final direction phải giải thích được mà không cần nhắc tên reference.

## Domain-artifact synthesis rules

- Artifact chỉ được giữ khi nó giải quyết một design problem: recognition, structure, information scent, comparison, orientation, brand memory hoặc journey logic.
- Phân biệt `form | structural | information | behavioral | ritual` transfer.
- Phân biệt fidelity `L0 reference | L1 cue | L2 structural | L3 direct form | L4 immersive`.
- Mặc định L1–L2; L3 khi object thật chính là product/decision object; L4 chỉ khi simulation/immersive experience có rationale mạnh.
- Không copy physical-world friction chỉ vì artifact ngoài đời có nó.
- Real branded products/documents phải dùng verified asset/spec hoặc label representative/concept/unknown.
- Semantic/accessibility experience không được phụ thuộc việc user nhận ra metaphor bằng mắt.

## Craft rules

- Không mọi section đều container + centered heading + 3 rounded cards.
- Không mọi page đều `copy left + image right`, full-bleed image overlay, hoặc một hero family duy nhất nếu page jobs khác nhau.
- Whitespace có rhythm, không chỉ “nhiều khoảng trắng”.
- Một visual device mạnh lặp có chủ ý tốt hơn 10 effect ngẫu nhiên.
- Brand color có role; không fill mọi thứ chỉ vì là primary.
- Image crop/safe zone là design decision.
- Typography phải readable với content thật và tiếng Việt/locale thực tế.
- Motion phải feedback/orientation/hierarchy/delight có kiểm soát.
- Không dùng trend như glass/gradient/oversized type chỉ vì reference dùng; trend phải phục vụ brand và hierarchy.
- Không dùng skeuomorphic texture/3D/material realism chỉ vì artifact source là physical.

## Pre-code visual gate

Không chuyển sang design-system/frontend implementation nếu chưa có:

- page-role composition matrix;
- 3 representative composition proofs/wireframes/mockups bằng text diagram, sketch, screenshot hoặc equivalent;
- one-sentence visual signature test: “nếu bỏ logo, người xem vẫn nhận ra project nhờ ___”;
- cross-page monotony check;
- mobile transformation cho các composition proof;
- `do / do not` đủ cụ thể để coder không quay về generic template.

Nếu project có rendered prototype sớm, ưu tiên render 2–3 representative page tops trước khi nhân rộng toàn site. Không implement 15 trang rồi mới phát hiện composition sai.

## Progressive resources

- [Visual craft reference](references/visual-craft-reference.md)
- [Visual direction gate](checklists/visual-gate.md)
- [Direction example](examples/direction-example.md)

## Output

`docs/visual-direction.md` hoặc equivalent gồm layout grammar, hierarchy, color/type roles, media direction, motion/depth rules, page-role composition matrix và do/don't.

Khi có reference benchmark, output nên thêm phần `Reference synthesis` ghi:

- reference role → principle extracted;
- adaptation cho project;
- rejected/non-transferable surface cues;
- constraints mobile/performance/accessibility.

Khi có domain-artifact research, output nên thêm phần `Artifact synthesis` ghi:

- artifact → design problem;
- transfer layer + fidelity;
- transferable vs rejected properties;
- brand/mobile/accessibility adaptation;
- real/concept/unknown asset status.

## Acceptance criteria

- Visual direction mô tả được bằng rules có thể implement.
- Có ít nhất 3 materially different page compositions proof-of-concept cho substantial multi-page redesign.
- Có page-role composition matrix trace được về user question + owner message.
- Brand/domain fit có rationale và evidence/inference được phân biệt.
- Mobile visual hierarchy được xem riêng, không chỉ shrink desktop.
- Art direction ảnh/icon rõ.
- Repetition được dùng để tạo consistency chứ không tạo template monotony.
- Primary pages khác task không bị ép vào cùng hero/top-of-page shell chỉ để code nhanh.
- Nếu dùng external references, direction là synthesis nguyên bản và không phụ thuộc việc clone một site.
- Nếu dùng domain artifacts, metaphor có task/mental-model rationale, lowest useful fidelity và do-not-copy boundary rõ.
