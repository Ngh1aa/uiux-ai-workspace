---
name: real-world-artifact-and-domain-metaphor-design
description: |
  Nghiên cứu vật thể, tài liệu, không gian, công cụ và nghi thức thật của một ngành để chuyển các mental model
  quen thuộc thành layout, component, information architecture, interaction và visual signature số có chủ đích.
  Dùng khi website cần thoát generic template, khi sản phẩm/dịch vụ có physical/domain artifacts mạnh (thẻ ngân hàng,
  vé, báo in, blueprint, menu, lookbook, hồ sơ, nhãn vận chuyển...), hoặc khi cần tạo Design DNA nguyên bản từ thế giới thật.
---

# Real-World Artifact & Domain Metaphor Design

## Goal

Bổ sung một nguồn design intelligence mà reference website thường bỏ qua:

`domain truth → real-world artifacts/rituals → user mental model → transferable properties → digital metaphor → brand/system adaptation → verification`

Không phải “làm website giống vật thật” một cách literal. Mục tiêu là dùng **familiarity** và **domain-native form language** để:

- tăng recognition / information scent;
- giảm generic AI-template feeling;
- làm visual language gắn với ngành và thương hiệu;
- chuyển mental model thật thành cấu trúc số dễ hiểu;
- tạo page/component compositions khác biệt nhưng vẫn usable.

Core rule:

> **Use the lowest metaphor fidelity that communicates the idea.**

Nếu chỉ cần tỷ lệ, grid, numbering hoặc hierarchy của artifact để truyền đạt ý tưởng thì không thêm texture/3D/animation giả vật lý.

## Why this works

Current design guidance consistently supports familiarity when it helps people predict behavior:

- Apple HIG 2026: familiarity means building on physical and digital concepts people already understand; metaphors should not be too literal or too abstract.
- Nielsen Norman Group: matching system to the real world and leveraging familiar real-world objects/activities can reduce learning burden, while failed skeuomorphism can confuse people.
- OOUX: structure experiences around objects in users' mental models before jumping directly to actions/flows.

These foundations support **functional metaphor and mental-model alignment**, not decorative nostalgia.

See [research foundations](references/research-foundations.md).

## Trigger rules

Activate when one or more are true:

- the domain has recognizable physical artifacts/documents/environments;
- the current UI is generic/card-heavy and brand/domain distinctiveness is weak;
- a product category maps naturally to an object users already know;
- a website can learn structure from offline media/service systems;
- user explicitly asks for “thiết kế giống sản phẩm thật”, “như tờ báo”, “như vé máy bay”, “như blueprint”, etc.;
- `design-reference-research-and-benchmark` found good digital references but visual direction still lacks ownable domain DNA;
- `brand-distinctiveness-and-visual-signature` needs domain-native recurring cues.

Usually skip for:

- local CSS bug;
- generic admin CRUD where a metaphor adds no clarity;
- flows where literal physical analogy would reduce usability;
- high-risk domains when the artifact could imply a false legal/security/system state.

## Inputs

Read before exploration:

- project truth / brand assets;
- audience and top tasks;
- domain playbook;
- product/service taxonomy;
- real product/assets available;
- content/data reality;
- accessibility/responsive/performance constraints;
- existing digital-reference benchmark if substantial redesign.

If real artifact/spec/brand asset is unknown, label it `UNKNOWN`; do not fabricate a “real” product.

## Artifact scope

Search beyond products. Candidate sources include:

### Physical objects
- cards, keys, devices, packaging, tools, machines, labels, badges, tickets.

### Printed/editorial artifacts
- newspaper, magazine, report, catalogue, menu, lookbook, brochure, passbook, receipt, certificate, timetable.

### Operational documents
- forms, statements, invoices, manifests, prescriptions, contracts, checklists, schedules, case files.

### Spatial/environmental systems
- signage, wayfinding, floor plan, blueprint, building directory, shelf/catalogue organization, service counter.

### Rituals and processes
- check-in, boarding, banking service, admission, ordering, delivery tracking, consultation, approval, handover.

### Domain-native digital artifacts
When the domain itself is digital, artifacts can be code editors, terminal logs, issues, commits, dashboards, timelines or media controls.

## Five transfer layers

Do not jump straight to visual imitation. Evaluate these layers separately.

### 1. Form metaphor
Transfer recognizable geometry/proportion.

Examples:
- bank card ratio → card-product presentation;
- boarding pass silhouette → trip confirmation;
- book cover → publication card;
- material swatch → furniture/material filter.

### 2. Structural metaphor
Transfer information composition rather than appearance.

Examples:
- newspaper → masthead + lead story + column hierarchy;
- annual report → institutional data/editorial rhythm;
- blueprint → plan/elevation-based real-estate navigation;
- menu → grouped restaurant offerings and hierarchy.

### 3. Information metaphor
Transfer object anatomy, attributes and relationships.

Example `Bank Card`:

```text
Object: Card
Attributes: network, tier, debit/credit, fee, eligibility, benefit
Relationships: account, customer, promotion
Actions: compare, apply, view details
```

This layer often improves IA even if the final UI does not visually resemble the physical object.

### 4. Behavioral metaphor
Transfer an understood action only when it predicts digital behavior.

Examples:
- flip a card → reveal secondary product information;
- swipe a ticket stack → browse passes;
- zoom/floor selection → inspect building availability.

Do not invent gestures that hide core actions or conflict with web conventions.

### 5. Ritual/process metaphor
Transfer the logic of an offline service journey.

Example banking:

`identify need → check eligibility → prepare documents → apply → verify → status/support`

Do not simulate physical bureaucracy if digital can remove unnecessary steps.

## Fidelity ladder

Choose the lowest useful level:

```text
L0 REFERENCE_ONLY   — research informs decisions but no visible metaphor
L1 CUE              — ratio, line, numbering, crop, material, icon or detail
L2 STRUCTURAL       — layout/information architecture follows artifact grammar
L3 DIRECT_FORM      — component visibly resembles the real artifact
L4 IMMERSIVE        — near-simulation; rare and requires strong rationale
```

Default toward `L1–L2`.

`L3` is appropriate when the object itself is the product/decision object and recognition is useful.

`L4` should be exceptional (interactive exhibit, simulation, virtual environment), never a default “wow effect”.

## Workflow

### Step 1 — Define the decision problem

Ask what the artifact should improve:

```text
recognition
product discovery
information hierarchy
brand memory
comparison
orientation
storytelling
interaction
service journey
```

Do not search physical references until the design problem is explicit.

### Step 2 — Build a domain artifact inventory

Create 8–20 candidates when scope justifies it.

| Artifact | Reality/source | User familiarity | Brand relevance | Task relevance | Potential layer |
|---|---|---:|---:|---:|---|

Use official product imagery/specs when a real branded product is involved.

### Step 3 — Map anatomy and behavior

For promising artifacts capture:

```text
purpose
parts/anatomy
information hierarchy
proportion/grid
materials/color cues
labels/naming
relationships
common actions
sequence/ritual
what users already know
what is merely decorative
```

### Step 4 — Score transfer potential

Default scorecard (100):

| Criterion | Weight |
|---|---:|
| User familiarity / mental-model fit | 20 |
| Task / information usefulness | 20 |
| Domain authenticity | 15 |
| Brand fit | 15 |
| Distinctiveness | 10 |
| Responsive feasibility | 5 |
| Accessibility clarity | 5 |
| Performance feasibility | 5 |
| Asset/content reality | 5 |

Reject even a high-aesthetic artifact if it harms task clarity or implies false reality.

### Step 5 — Select transfer layer + fidelity

For each finalist explicitly state:

```text
Artifact:
Problem it solves:
Transfer layer:
Fidelity: L0-L4
Keep:
Do not copy:
Digital adaptation:
Brand adaptation:
Mobile adaptation:
Accessibility/performance caveat:
Reality/evidence status:
```

### Step 6 — Synthesize, do not theme-park

Limit major page/system to a small coherent set of cues.

A site should not become:

```text
card object + newspaper + ticket + blueprint + receipt + notebook
```

all on one page merely because each metaphor is clever.

Choose a dominant domain grammar and a few supporting artifacts.

### Step 7 — Handoff

Feed outputs into:

- `brand-distinctiveness-and-visual-signature` for recurring ownable cues;
- `visual-design-direction` for layout/type/color/media grammar;
- `design-system-and-components` for tokens/components/patterns;
- `interaction-patterns-and-form-ux` when a ritual maps to a flow;
- `reference-analysis-and-design-to-code` when a verified artifact/reference must be translated into implementation.

## Domain starter matrix

Use only as search prompts, not prescribed styles.

| Domain | Candidate artifacts |
|---|---|
| Banking | card, statement, passbook, receipt, exchange board, branch signage, annual report |
| News/media | newspaper masthead, columns, section rules, dateline, magazine cover |
| Education | timetable, yearbook, ID card, report card, campus map, notebook |
| Real estate/building | blueprint, floor plan, elevation, directory, leasing brochure, material sample |
| Furniture/interior | catalogue, swatch, specification sheet, room plan, material board |
| Fashion | garment label, lookbook, tag, fabric swatch, pattern, editorial magazine |
| Hospitality | room key, concierge book, booking confirmation, menu, luggage tag |
| Travel/airline | boarding pass, passport, departure board, route map, baggage tag |
| Logistics | parcel, shipping label, barcode, manifest, tracking route |
| Automotive | instrument cluster, spec sheet, key fob, workshop manual |
| Healthcare | appointment card, patient chart, prescription, lab report |
| Government | official form, certificate, notice, stamp/seal hierarchy, service counter |
| Museum/culture | exhibit label, archive card, ticket, catalogue, museum map |
| Developer/SaaS | terminal, editor, issue, commit, log, deployment timeline |

## Banking example: “Open a card”

Strong approach:

- study actual current branded cards;
- use card proportion/anatomy as recognition cue;
- map real network/tier/product attributes;
- keep digital CTA obvious;
- adapt on mobile without forcing tiny unreadable card text.

Weak approach:

- create fake `BANK NAME / 1234 5678` card;
- add plastic reflections/3D tilt just to mimic a card;
- show fake Visa/Mastercard/Napas marks;
- imply a product exists when official catalogue does not support it.

See [banking example](examples/banking-artifact-example.md).

## Anti-patterns

- literal skeuomorphism for decoration only;
- fake leather/paper/metal textures without functional meaning;
- copying trademarks, card art, stamps, tickets or proprietary objects without permission/source;
- fake account/card numbers presented as real customer data;
- metaphor that changes conventional control meaning;
- physical constraints carried into digital even when they are unnecessary;
- novelty interaction that hides CTA/navigation;
- forcing one artifact metaphor onto every page;
- mobile shrinking a desktop physical replica;
- using a concept/mock artifact as evidence of a real product;
- making accessibility depend on recognizing the visual metaphor.

## Reality / trust rules

If the artifact represents a real product, legal document, credential, ticket, financial instrument or official certificate:

- verify current official source/assets/specs;
- label `REAL | REPRESENTATIVE | CONCEPT | UNKNOWN`;
- never fabricate official marks or system states;
- do not show realistic sensitive data unless explicitly safe/test data;
- preserve required legal/network marks only when authorized and accurate.

Route `trust-credibility-and-transparency`, `security-and-privacy` or `system-reality-and-production-readiness` when stakes justify it.

## Responsive rules

Metaphor fidelity may change by breakpoint.

Example:

```text
Desktop: L3 direct card form
Mobile: L2 structured card row
Screen reader: semantic product object + attributes + actions
```

The semantic experience must not depend on physical resemblance.

## Output

Create `docs/real-world-artifact-design.md` or equivalent:

```md
# Real-World Artifact Design

## Design problem
## Domain artifact inventory
## Finalists + score
## Artifact anatomy
## Transfer layers
## Fidelity decisions
## Design DNA extracted
## Brand adaptation
## Page/component applications
## Mobile/accessibility adaptation
## Reality / asset constraints
## Do-not-copy list
## Handoff rules
```

## Quality gate

Pass only when:

- [ ] artifact/domain source is real or explicitly labeled concept/unknown;
- [ ] user familiarity and task relevance are explained;
- [ ] transfer layer is explicit;
- [ ] fidelity level is explicit;
- [ ] transferred properties and rejected properties are both documented;
- [ ] metaphor improves recognition/structure/brand/task, not just aesthetics;
- [ ] digital conventions remain recognizable;
- [ ] mobile adaptation exists;
- [ ] accessibility does not depend on the visual metaphor;
- [ ] performance/asset feasibility is considered;
- [ ] no fake branded/official product is presented as real;
- [ ] final system is coherent rather than a collage of clever metaphors.

## Completion rule

Do not claim a metaphor “improves UX” from resemblance alone. State the mental-model hypothesis, what was transferred, why it is expected to help, and what validation/evidence would confirm it.
