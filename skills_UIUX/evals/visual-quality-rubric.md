# Visual Quality Eval Rubric — V5.4

Chuyên dùng để chấm **visual output quality** của website được tạo/redesign bởi agent. CI chứng minh "không hỏng"; rubric này chứng minh "đẹp, đọc được và ổn định hơn".

## Grading approach

1. **Deterministic gates** (pass/fail — machine verifiable khi tooling cho phép):
   - Route renders without runtime crash
   - Required pages exist and load
   - Screenshots captured for evidence
   - No horizontal overflow at standard/declared viewports
   - Media assets not broken (no 404, no missing `<img>`)
   - Viewport meta tag present where applicable
   - Build/runtime usable
   - Shared-owner route coverage exists when a shared header/footer/theme/button/surface changed
   - Computed rendered text/control states do not collapse to effectively invisible foreground/background pairs

2. **Model/human judgment** (0–4 scale per dimension):
   - Requires rendered screenshots or live page
   - Model grader provides initial score
   - Human review calibrates and validates

> **Note**: Không hard-check CSS custom properties hay font-family declarations. Website đẹp hoàn toàn có thể dùng `system-ui`. Next.js/React có thể không có `.html` tĩnh để analyze. Automated contrast checks are regression signals, not formal WCAG conformance claims.

## Elementary visual sanity pre-gate

Before scoring dimensions, inspect actual rendered evidence for:

- important text that is only readable after selection/highlight;
- white-on-white / dark-on-dark / effectively `1:1` text or control labels;
- default/hover/focus/active/disabled labels that disappear;
- shared light↔dark surface changes that leave stale inherited foreground/link/icon states;
- cascade/specificity where computed style contradicts intended component/token color;
- human/primary focal subject crop that cuts face/head/identifying feature without art-direction rationale.

If any DUE-NOW P0/P1 item above remains, the visual-quality eval **FAILS regardless of composite score**.

## 7 Dimensions — 0–4 scale

### 1. Hierarchy & information architecture — 20%

- 0: no discernible visual hierarchy; all elements compete equally.
- 1: basic heading size difference but priority unclear.
- 2: hierarchy exists but inconsistent across sections; some competing elements.
- 3: clear primary/secondary/tertiary hierarchy; CTA prominence appropriate.
- 4: hierarchy perfectly supports user scanning and task completion; content priority matches business/user goal; entry points clear at every scroll depth.

### 2. Typography system — 15%

- 0: browser defaults throughout; no intentional type system.
- 1: single font applied but no scale/rhythm.
- 2: basic scale (2–3 sizes) with reasonable readability.
- 3: considered type system with proper scale, line height, measure; distinct heading/body/caption roles.
- 4: polished typographic rhythm; pairing has character and rationale; micro-typography appropriate; type reinforces brand voice.

### 3. Media & art direction — 15%

- 0: broken images, placeholder boxes, irrelevant stock, or primary human/focal subject badly cropped.
- 1: images present but generic stock with no cropping consideration.
- 2: relevant images with basic sizing; some crop/aspect issues.
- 3: images support content; consistent aspect ratios; appropriate sizing; focal subjects survive declared viewports.
- 4: art direction has clear intent; crops highlight subject; media-to-copy relationship considered; images contribute to brand narrative; no watermarks or obviously broken AI artifacts; responsive art direction is used when one crop cannot serve all target ratios.

### 4. Page-role diversity — 15%

- 0: all pages are visually interchangeable (same hero → cards → CTA).
- 1: minor variations (different hero image) but same skeleton.
- 2: 2 distinct compositions for 5+ page roles.
- 3: 3+ distinct composition families; page structure reflects content purpose.
- 4: each page role has composition optimized for its user task; homepage ≠ about ≠ services ≠ project detail; cross-page coherence maintained through system, not template cloning.

Automated signal: `scripts/template-monotony-detector.py` provides structural diversity data.

### 5. Responsive transformation — 10%

- 0: broken at in-scope narrow widths; horizontal scroll; unreadable.
- 1: content reflows but no intentional adaptation.
- 2: basic responsive; stacks to single column with acceptable results.
- 3: breakpoint-appropriate layout changes; touch targets adequate; navigation adapts.
- 4: mobile has intentional re-composition when mobile is in scope; critical actions accessible; media/type adapts; mobile-specific interaction patterns where appropriate.

### 6. Brand distinctiveness — 15%

- 0: could be any website; no brand expression.
- 1: logo present but design is generic template.
- 2: brand colors applied but interchangeable with a different logo.
- 3: consistent brand expression; recognizable color/type/imagery system.
- 4: design is recognizable with logo hidden; visual signature extends beyond color; brand personality expressed through composition, motion, imagery style and interaction character.

### 7. Anti-generic-AI — 10%

- 0: obvious AI-template: glass cards, gradient borders, rounded everything, identical section spacing, over-decorated.
- 1: 3+ generic AI patterns present; decorative gradients, unnecessary blur effects.
- 2: mostly clean but 1–2 template-ish patterns.
- 3: purposeful design choices; decoration justified by function.
- 4: no template smell; design choices are specific to the domain/brand/content; ornamentation serves hierarchy or brand, never filler.

## Composite score

```
score = sum(dimension_score × dimension_weight) / 4 × 100
```

Range: 0–100.

## Hard fail triggers

Regardless of dimension scores, the visual quality eval FAILS if:

- Important text/CTA/icon is effectively invisible on its rendered surface or requires selection/highlight to read
- A shared surface/theme change causes stale inherited foreground colors across affected routes
- A visible button/control label disappears in default/hover/focus/active/disabled state
- A primary human/focal subject is unjustifiably cropped through face/head/identifying feature at a declared target viewport
- All primary pages share the same hero+cards+CTA silhouette without rationale
- Stock photos with visible watermarks on hero/primary images
- Mobile is pure column-stack of desktop with zero layout adaptation **when mobile is in declared scope**
- Critical content/CTA is invisible or unreachable without horizontal scroll
- Page has no visible content (blank, all-white, all-black)
- Brand assets are from a different company/industry
- Screenshot is obviously broken but accepted because build/CI/DOM/pixel-diff metrics passed

## Grading protocol

1. Run elementary visual sanity pre-gate.
2. Deterministic gates — any gate failure → score capped at 30 and overall FAIL when it is a DUE-NOW P0/P1.
3. Capture screenshots for declared representative viewports/page roles.
4. For shared owner changes, run elementary sanity across all affected routes/templates; deep aesthetic scoring may use representative routes.
5. Score each dimension 0–4.
6. Compute composite score.
7. Check hard fail triggers.
8. Record confidence: `high` (clear) / `medium` (borderline) / `low` (needs human).
