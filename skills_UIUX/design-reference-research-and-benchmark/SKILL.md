---
name: design-reference-research-and-benchmark
description: |
  Tìm, sàng lọc và benchmark website/design reference theo ngành, audience, business goal, brand,
  page role và implementation reality trước khi khóa visual direction. Dùng cho redesign/new site hoặc
  khi UI đang generic và cần reference intelligence có căn cứ thay vì moodboard cảm tính.
---

# Design Reference Research & Benchmark

## Goal

Biến “tham khảo website đẹp” thành evidence cho **design decisions cụ thể**:

`project truth → decision problem → source mix → candidate pool → page/state inspection → scoring → principle extraction → page-role adaptation → visual-direction handoff`

Không chọn reference chỉ vì đẹp. Không copy một website. Không dùng gallery shot như bằng chứng UX.

## 1. Required inputs

Đọc trước khi research:

- owner/business goal + conversion;
- audience/top tasks/entry context;
- user journey;
- domain playbook;
- brand source status + assets;
- sitemap/page roles;
- content/image/data reality;
- responsive/accessibility/performance constraints;
- preserve list nếu redesign.

Nếu thiếu các input làm thay đổi decision, giữ `UNKNOWN/ASSUMPTION`; không search bằng adjective cảm tính để bù lỗ hổng.

## 2. Classify the reference problem

Không search chung chung. Ghi rõ decision đang cần evidence, ví dụ:

- whole-site information architecture;
- homepage orientation;
- location page;
- specification/product page;
- evidence/ESG page;
- amenities/experience page;
- availability/search page;
- conversion/contact page;
- navigation;
- typography/editorial grammar;
- photography/media;
- motion;
- mobile behavior.

Mỗi materially different page role có thể cần reference role khác nhau.

## 3. Source hierarchy

### Tier A — real production/category sites
Dùng mạnh cho IA, journey, trust, content priority, conversion, responsive behavior và practical task design.

### Tier B — curated/award sites
Dùng cho art direction, composition, typography, storytelling, motion. Award status không chứng minh usability/conversion/accessibility.

### Tier C — case-study/designer platforms
Dùng cho system/component/brand translation; label production vs concept.

### Tier D — mood/editorial/photography/physical references
Dùng cho imagery, graphic language, texture, spatial/editorial cues; không dùng làm nguồn chính cho UX flow.

## 4. Search strategy

Tạo ít nhất 3 query families:

1. Industry/category reality.
2. Page-role/task-specific patterns.
3. Visual/art-direction patterns.

Với whole-site redesign, search **theo page role**, không chỉ homepage/hero.

Ví dụ real estate:

- commercial office location page;
- office floor plan/specification website;
- building amenities experience;
- sustainability evidence property site;
- office availability/leasing UX.

## 5. Candidate pool

Cho substantial redesign, mặc định 10–20 candidate có mix:

- 4–8 production/category competitors/peers;
- 3–6 best-in-class craft references;
- 2–4 cross-industry references cho một pattern cụ thể;
- optional domain artifacts/mood references.

Chất lượng > số lượng.

## 6. Inspect actual pages/states, not homepage thumbnails

Với candidate được dùng cho material decision, ghi rõ page/state đã inspect.

Nếu tooling cho phép, capture/open screenshot hoặc rendered page evidence. Không kết luận cả design system từ một hero screenshot.

Reference record:

| Reference | Type | Page/state inspected | User task | Principle | Caveat | Confidence |
|---|---|---|---|---|---|---|

## 7. Reject weak references early

Reject nếu:

- đẹp nhưng không fit audience/business/task;
- chỉ có perfect fake content;
- mobile/interaction khó adapt;
- phụ thuộc 3D/video/assets project không có;
- concept bị dùng như production UX proof;
- brand-specific surface quá mạnh để transfer;
- không giúp decision đang nghiên cứu;
- chỉ cung cấp thêm một generic hero/card pattern vốn đã quá phổ biến.

## 8. Score finalists

Scorecard mặc định 100:

| Criterion | Weight |
|---|---:|
| Domain/page-role fit | 20 |
| Audience/top-task fit | 15 |
| Business/conversion fit | 15 |
| Brand fit | 15 |
| UX/information usefulness | 10 |
| Composition usefulness | 10 |
| Visual craft | 5 |
| Interaction/motion | 5 |
| Implementation feasibility | 5 |

Score hỗ trợ critique, không thay critique.

## 9. Select references by role

Chọn 3–6 finalist nhưng **không yêu cầu một site làm mọi thứ**.

Ví dụ:

- A — IA/navigation;
- B — location/map composition;
- C — specification/floor-plan hierarchy;
- D — evidence/ESG storytelling;
- E — amenities/workday imagery;
- F — conversion/mobile.

## 10. Page-role reference matrix — bắt buộc cho whole-site redesign

| Page role | User question | Reference(s) used | Principle extracted | What NOT to copy | Project-specific adaptation |
|---|---|---|---|---|---|

Nếu nhiều materially different page roles đều map về cùng một hero/layout principle mà không có rationale, benchmark **FAIL** vì chưa tạo đủ design intelligence.

## 11. Extract principles, not surfaces

Mỗi finalist phải trả lời:

```text
What works?
Why does it work for that audience/task?
What is transferable?
What is brand-specific/non-transferable?
What should be rejected?
How is it adapted to our content/assets/brand?
How does mobile change it?
What are performance/accessibility constraints?
```

Không dùng “inspired by X” làm rationale cuối.

## 12. Cross-reference synthesis

Trước handoff sang `visual-design-direction`, synthesize:

- layout grammar;
- page-role diversity;
- hierarchy/type;
- color/surface roles;
- imagery/media;
- domain-native decision objects;
- trust/conversion;
- motion;
- mobile.

### Anti-Frankenstein rule

Mỗi principle được chọn phải thuộc cùng một final design DNA. Nếu A/B/C reference tạo ba visual languages không thể hòa giải, reject bớt thay vì ghép tất cả.

## 13. Output

Tạo `docs/design-reference-benchmark.md` hoặc equivalent:

```md
# Design Reference Benchmark

## Project decision
- Business goal:
- Audience/top tasks:
- Brand constraints:
- Page roles:
- Content/assets reality:

## Search strategy
- Decision problems:
- Query families:
- Source mix:

## Candidate pool
| Reference | Type | Pages inspected | Role | Score | Keep/Reject | Reason |

## Final references
### Reference A — <job>
- Pages/states inspected:
- Principle:
- Why it works:
- Do not copy:
- Project adaptation:
- Mobile/performance/a11y caveat:

## Page-role reference matrix
...

## Extracted Design DNA inputs
- Layout grammar:
- Page-role composition opportunities:
- Type:
- Color/surface:
- Media:
- Domain objects:
- Interaction:
- Conversion/trust:

## Rejected patterns
...

## Handoff to visual-design-direction
...
```

## 14. Quality gate

PASS chỉ khi:

- [ ] Có production/category references, không chỉ gallery.
- [ ] Reference research bám business/user/page-role problem.
- [ ] Material finalists có actual page/state inspection khi accessible.
- [ ] 3–6 finalists có job rõ.
- [ ] Production/concept distinction rõ.
- [ ] Có page-role reference matrix cho substantial multi-page redesign.
- [ ] Không lấy một universal hero/layout làm giải pháp mặc định cho mọi page.
- [ ] Principle + do-not-copy + adaptation được ghi.
- [ ] Mobile/performance/accessibility feasibility đã xét.
- [ ] Output đủ cụ thể để visual-design-direction tạo 3+ representative compositions khi site có nhiều page role.

## Completion rule

Không nói reference “tốt nhất” hay “UX tốt” chỉ vì award. Không chuyển sang code trực tiếp từ benchmark. Benchmark phải đi qua `visual-design-direction`/Design Contract trước substantial implementation.
