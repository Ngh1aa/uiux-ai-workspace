# Visual Taste Calibration — External Source Synthesis

Source reviewed: Anthropic `frontend-design`, pinned at `85cce0381e7860082641b59d961a2b8c368b8b79` (Apache-2.0). This file is an adapted synthesis for `skills_UIUX`; project truth and the Design Contract remain authoritative.

## Why this exists

`visual-design-direction` already owns visual grammar. This reference adds a stricter **anti-generic calibration pass** so a coherent design does not accidentally collapse into common AI/template defaults.

## Calibration rules

### 1. Start from subject matter, not style adjectives

Before choosing palette/type/layout, identify the project's actual world: product, audience, material/physical cues, content density, decision objects, trust needs and cultural context. A distinctive direction should be explainable from those inputs.

Reject a direction that could be reused unchanged for a materially different industry merely by swapping logo and copy.

### 2. Make one memorable visual commitment

Choose one primary distinctive device and let the rest of the system support it. Examples: an ownable type treatment, a domain-native composition, a distinctive media behavior, a specific spatial/grid grammar, or one orchestrated motion moment.

Do not stack multiple attention devices simply to appear “premium”.

### 3. Treat typography as visual structure

- choose type deliberately for content/brand/domain, not because it is the model's default;
- define role, scale, width/weight and line-length behavior;
- let display typography participate in composition when appropriate;
- avoid decorative labels/eyebrows/all-caps conventions that do not encode useful information;
- verify real locale/content, especially Vietnamese diacritics and long labels.

### 4. Structural decoration must encode meaning

Borders, numbering, dividers, badges, rules, arrows and meta labels should communicate sequence, hierarchy, state or grouping. If removing a device does not reduce comprehension/identity, question whether it belongs.

### 5. Avoid generic composition tells

Before code, explicitly challenge defaults such as:

- universal centered hero + gradient + stats;
- identical rounded card grids for unrelated content;
- repeated `eyebrow → H2 → paragraph` section headers;
- automatic split-screen text-left/image-right on every page;
- numbering decorative sections that are not sequential;
- the same radius/shadow/depth treatment at every hierarchy level;
- scattered fade-and-slide-up reveals on every section.

These patterns are not forbidden. They require task/brand/content rationale.

### 6. Motion is hierarchy and feedback

Non-user-triggered motion should be rare and orchestrated. Prefer one meaningful entrance/reveal system over many independent effects. Interaction-triggered motion may explain state change, continuity, confirmation or orientation. Always respect reduced motion.

### 7. Run a two-pass direction critique

**Pass A — plan**

Create a compact direction covering:
- 4–6 core color roles;
- typography roles;
- layout/composition concept;
- one memorable visual commitment;
- motion/depth rules;
- do/do-not rules.

**Pass B — anti-template critique**

For every free design axis, ask:
1. Is this choice derived from project truth or a familiar default?
2. Would the same choice appear in an unrelated SaaS/portfolio/hotel site?
3. What would a stronger subject-matter-specific choice be?
4. Does the revised choice remain usable, accessible and implementable?

Only then lock the direction in the Design Contract.

## Verification

For substantial design work, evidence should include:

- representative page-role compositions;
- cross-page monotony comparison;
- rendered screenshots when implementation exists;
- a one-sentence visual-signature test;
- proof that the memorable device survives without depending on the logo alone.

Do not call a direction “distinctive” solely because it uses unusual colors, fonts or animation.
