---
name: motion-component-intelligence
description: |
  Dùng Motion Primitives như một local upstream corpus để tìm, đánh giá và adapt motion/component
  patterns cho website hoặc product UI. Kích hoạt sau project truth và art direction; không dùng như
  template engine. Bắt buộc kiểm tra stack, purpose, performance, reduced-motion, provenance và visual fit.
---

# Motion Component Intelligence

## Purpose

Skill này nối UIUX Factory với upstream corpus:

`skills_UIUX/upstream/motion-primitives-website`

Corpus là **design/implementation intelligence**, không phải source of truth của project. Source of truth vẫn là project code, Design Contract, design system, content, accessibility và product intent.

## Activation

Dùng khi ít nhất một điều đúng:

- Design Contract cần motion/signature interaction rõ ràng;
- một screen cần scroll choreography, state transition, spatial continuity, interactive card/media, 3D/WebGL hoặc expressive hero;
- implementation cần reference React/Framer Motion/GSAP/Three.js đủ gần để adapt an toàn;
- visual critique chỉ ra UI tĩnh, generic hoặc thiếu interaction hierarchy.

Skip khi:

- task chỉ là data/table/form correctness;
- motion không giải quyết feedback, continuity, hierarchy, state change hoặc signature moment;
- target stack không phù hợp và việc port pattern tạo complexity lớn hơn giá trị;
- reduced-motion/performance budget chưa có cách đáp ứng.

## Mandatory order

1. **Project truth first** — đọc stack, components, tokens, page role, current behavior, constraints.
2. **Motion job** — ghi rõ animation phục vụ feedback / continuity / hierarchy / state change / delight.
3. **Query corpus narrowly** — dùng helper `core.orchestration.motion_component_intelligence` hoặc search trực tiếp upstream theo 1 intent chính.
4. **Shortlist tối đa 3 candidates** — không browse cả catalog rồi nhồi nhiều effect.
5. **ADOPT / ADAPT / REJECT** từng candidate theo project fit.
6. **Check stack/dependencies** — React/Next/Tailwind/Framer Motion/GSAP/Three/Spline chỉ được thêm khi target thực sự cần.
7. **Translate to Design Contract** — lock trigger, from/to state, duration/easing, responsive behavior, reduced-motion behavior.
8. **Implement locally** — copy/port chỉ phần cần thiết; đổi naming/tokens/API để khớp project. Không tạo parallel design system.
9. **Verify rendered reality** — keyboard/focus, mobile, reduced motion, scroll performance, CLS, animation lifecycle.
10. **Record provenance** — upstream path + pinned commit + adaptation rationale.

## Retrieval helper

From `uiux-factory/`:

```python
from core.orchestration.motion_component_intelligence import MotionPrimitiveCatalog

catalog = MotionPrimitiveCatalog()
results = catalog.search("editorial image reveal scroll", limit=3)
for item in results:
    print(item.path, item.category, item.dependencies, item.score)
```

The helper ranks component source paths by filename/category/content signals. It does **not** decide that a component should be used.

## Stack policy

### React / Next.js

May adapt source directly after checking versions and dependencies.

### HTML/CSS/JS, Vue, Svelte or other stack

Treat upstream implementation as a behavioral reference. Port the interaction using the target stack instead of dropping `.tsx` files into the project.

### Heavy dependencies

GSAP, Three.js, React Three Fiber, Spline or shader/WebGL code require a material visual reason. Do not add them for a minor hover.

## Component budget

Default per page/flow:

- 0–1 signature primitive;
- 0–2 supporting motion primitives;
- normal controls should stay native to the project design system.

A page that visibly looks like a component-library demo fails this skill.

## Selection rubric

| Criterion | Question |
|---|---|
| Product fit | Does it improve the actual user task or product story? |
| Art-direction fit | Does it reinforce the approved visual signature? |
| Distinctiveness | Is it less generic than the current treatment without becoming gimmicky? |
| Stack fit | Can it be implemented without fighting the target architecture? |
| Performance | Can it stay smooth and bounded on representative devices? |
| Accessibility | Is reduced motion and keyboard/focus behavior explicit? |
| Responsive fit | Does the interaction transform intentionally below desktop? |

Reject candidates with weak product/art-direction fit even if visually impressive.

## Adaptation rules

- Replace hard-coded colors/type/radius/spacing with project tokens.
- Preserve semantic HTML and focus order.
- Remove decorative loops when offscreen.
- Avoid `transition: all` and unbounded scroll listeners.
- Prefer transform/opacity unless the effect specifically needs canvas/WebGL.
- Do not copy demo content, logos, artwork or brand treatment.
- Do not ship example-only assets without explicit provenance/license review.
- Keep interaction state deterministic and testable.

## Reduced-motion contract

Every adopted primitive must define one of:

- **instant state** — no spatial animation;
- **opacity-only fallback** — short fade without parallax/zoom;
- **static composition** — signature visual remains legible without motion.

Never hide content or functionality when motion is reduced.

## Provenance record

For each adopted primitive, record:

```text
source: skills_UIUX/upstream/motion-primitives-website/<path>
upstream_commit: pinned gitlink SHA
decision: ADOPT | ADAPT
purpose: <motion job>
adaptation: <tokens/stack/behavior changes>
verification: <routes/viewports/reduced-motion evidence>
```

## Project-family routing heuristics

These are defaults, not requirements:

- **Luxury/editorial/architecture** → scroll, media reveal, spatial/card interaction; allow one stronger signature primitive.
- **Automotive/mobility** → route/progression, product reveal, 3D only when it clarifies product/story.
- **Enterprise/fintech/risk** → restrained state transitions, feedback, disclosure; avoid decorative shader noise.
- **Education** → progression, feedback and concept continuity; avoid attention-stealing loops.
- **AI tooling** → generation/progress/state choreography, code/artifact transitions, command feedback.

## Acceptance criteria

- [ ] Motion purpose is explicit.
- [ ] No more than 3 upstream candidates were shortlisted for a local decision.
- [ ] Candidate decision is ADOPT / ADAPT / REJECT with rationale.
- [ ] Target stack and dependency impact were checked.
- [ ] Project tokens and semantics own the final component.
- [ ] `prefers-reduced-motion` behavior exists.
- [ ] Responsive transformation is intentional.
- [ ] Rendered performance/interaction was verified where the component is used.
- [ ] Upstream path and pinned commit are traceable.
- [ ] Final page does not read like a component-library showcase.
