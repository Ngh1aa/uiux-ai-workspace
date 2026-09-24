---
name: prototype-visual-experience-qa
description: |
  Quality framework for HTML/CSS/JS visual and interactive prototypes. Use when the goal is
  to make a prototype feel immediately clear, distinctive, polished and demo-ready before
  production concerns dominate. It complements, not replaces, accessibility, responsive,
  domain, content, research and production-readiness skills.
---

# Prototype Visual Experience QA

## Scope

Use for `visual-prototype` and `interactive-prototype` work where the primary deliverable is
the rendered experience a reviewer can see and interact with.

Do **not** use this skill to claim production readiness, legal compliance, SEO completeness,
backend correctness or business validation.

The core sequence is:

`audience/context → intended impression → site archetype + vertical + page role → demo path →
signature moment → visual system → states/motion → rendered critique → revise`

## 1. Understand before composing

Record before visual composition:

- who is evaluating the prototype and what they need to understand;
- the intended first-impression sentence for roughly the first 3 seconds;
- website archetype, vertical/sub-industry and representative page roles;
- exactly 3 useful style adjectives;
- the demo path from entry to completion;
- one signature/hero moment worth disproportionate craft;
- content/media reality and important unknowns.

Do not choose a universal layout family merely because the project is "ecommerce", "SaaS",
"hotel", etc. Domain research and page-role tasks remain authoritative.

## 2. Familiarity versus differentiation

Preserve familiar interaction grammar where it protects comprehension: navigation, search,
checkout, forms, account actions and platform conventions should not be reinvented without
evidence.

Differentiate through art direction, content hierarchy, composition, typography, imagery,
motion and a project-specific visual signature.

### Anti-generic check

Actively inspect for:

- repeated rounded cards with identical shadow/radius treatment;
- every section using the same centered heading + cards composition;
- cream + serif or black + neon being used without brand/domain rationale;
- all-caps micro-labels attached to every section;
- decorative dashboard/product mockups that do not prove anything;
- identical fade/slide animation on every section;
- generic stock media that could belong to any industry.

If the page could be relabelled for another industry without changing its composition/media,
the direction is still too generic.

## 3. Interaction heuristics

Use established UX principles as critique prompts, not as mechanical laws.

- Choice complexity: reduce or group competing choices when scanning becomes difficult.
- Target acquisition: primary controls must be easy to hit and separated from destructive or
  secondary actions.
- Familiar patterns: preserve conventions unless the benefit of deviation is clear.
- Grouping: proximity, similarity and alignment should reveal relationships without extra text.
- Salience: one primary action or decision object should visually win where a decision is needed.
- Feedback: clicks, submits, toggles and validation must visibly respond.
- Multi-step progress: when completion requires several steps, show state/progress if it reduces
  uncertainty.
- Aesthetic quality must not conceal a confusing flow.

### Touch-target nuance

For prototype craft, prefer approximately `44 × 44 CSS px` or larger for important touch
controls when space allows.

Do not misstate this as the WCAG 2.2 AA minimum. WCAG 2.2 SC 2.5.8 uses a `24 × 24 CSS px`
minimum target-size requirement with documented exceptions; `44 × 44 CSS px` belongs to the
enhanced AAA criterion. Always route formal accessibility claims through the accessibility skill.

## 4. Visual system

### Colour

- Define primary, supporting, neutral and semantic roles.
- Use accent colour intentionally; do not make every component compete for attention.
- Verify readable contrast through the accessibility skill, not by visual intuition alone.

### Typography

- Typography must support the 3 style adjectives and content hierarchy.
- Prefer a restrained font system; add typefaces only when they have a clear role.
- Use a coherent type scale, line-height and measure.
- Treat approximate ranges such as 65–80 characters for long-form body copy as heuristics,
  not universal pass/fail rules.

### Layout and spacing

- Shared alignment and spacing rhythm must be obvious across representative pages.
- Whitespace is useful when it improves hierarchy; large empty regions are not automatically
  "premium".
- Run a squint/blur review: the intended decision object and primary action should remain obvious.
- Page roles must be compositionally different when their user tasks are materially different.

### Media

- Every image/illustration/icon family needs a job and consistent art direction.
- Prefer domain-relevant, content-relevant media over generic stock.
- Verify crops and focal subjects at rendered breakpoints.
- The primary decision object must receive the visual dominance appropriate to the domain.
- Include at least one memorable, brief-specific visual signature when it supports the brand.

## 5. Motion and microinteraction

Choose one primary motion/signature interaction to receive the highest polish. Keep the rest
supportive.

- Hover/press/focus states must exist for interactive controls used in the demo.
- Typical UI transitions around 150–300 ms are a starting heuristic, not a universal requirement.
- Avoid broad scroll-triggered animation applied identically to every section.
- Loading, success, error and validation feedback must be visible when the demo path invokes them.
- Respect `prefers-reduced-motion` when motion is material.
- Custom cursor/parallax effects require a clear experience rationale and must not reduce control.

## 6. Component and state completeness

For every component appearing in the representative flow, verify the states that can actually
occur:

- default;
- hover/pressed;
- focus-visible;
- selected/active;
- disabled when applicable;
- loading where waiting exists;
- empty/no-results where lists can be empty;
- error and success for forms/actions.

Do not fabricate states that the prototype cannot reach merely to make a checklist look complete.

## 7. Responsive strategy

Decide explicitly whether the prototype is presentation-only at one viewport or intended to work
across devices.

When responsive demonstration is required, inspect representative widths near mobile, tablet and
desktop rather than trusting CSS breakpoints alone. Around 375, 768 and 1440 CSS px are useful
pressure-test sizes, not universal device standards.

Check:

- content priority transforms intentionally;
- navigation and filters remain usable;
- media crops preserve focal subjects;
- controls remain reachable;
- long/translated/Vietnamese content does not break the composition.

## 8. Rendered self-critique

Before calling a prototype finished, perform:

### Squint test
Blur/squint each representative screen. Record what wins first, second and third.

### 5-second comprehension prompt
Ask what a new viewer should be able to identify quickly:
- what this site/product/service is;
- who it is for;
- what the primary next action or decision is.

Treat this as a usability-research prompt, not an automated truth claim unless actual participants
were tested.

### Remove-one-decoration pass
Identify one decorative item that can be removed without losing meaning. If nothing can be removed,
justify why the visual density is intentional.

### Style-word check
Compare the render to the 3 chosen adjectives using concrete evidence from type, colour, media,
spacing and motion.

### Competitive distinctiveness check
Place representative screenshots beside selected production references. The goal is not to be
"more decorated"; identify the project-specific difference and verify it does not harm task clarity.

### Real interaction pass
Complete the demo path with mouse/keyboard and touch emulation where relevant.

### Content stress test
Use real or realistic copy, Vietnamese diacritics when applicable, long names, large values and
edge-case labels.

## 9. Evidence gate

PASS only when:

- [ ] website archetype, vertical and representative page roles are explicit;
- [ ] intended first impression and 3 style adjectives are documented;
- [ ] one demo path and one signature moment are identified;
- [ ] domain/reference research informed composition instead of a universal template;
- [ ] representative rendered screenshots/states were actually inspected;
- [ ] squint hierarchy matches the intended decision order;
- [ ] media is domain-relevant and crop-safe;
- [ ] obvious generic/AI-template repetition was actively challenged;
- [ ] focus/hover/press and demo-relevant loading/error/success states are present;
- [ ] responsive intent is explicit and tested where required;
- [ ] 5-second comprehension questions are defined, and any claim of user success is backed by
      actual participant evidence;
- [ ] prototype limitations are stated truthfully.

## Completion rule

A clean build, a screenshot file, or a high deterministic score is not sufficient evidence that
the prototype is visually strong. If rendered review says the experience is generic, the owning
art-direction/composition decision must be reconsidered before adding another CSS override layer.
