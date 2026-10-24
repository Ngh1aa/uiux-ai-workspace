# Visual brief: UX → UI handoff

The one page a visual designer (or Claude Design) receives after UX Readiness passes.
It fixes what must not change and frees what should be explored.

**Product:** **UX Readiness verdict:** READY / READY_WITH_RISKS **Record:** `docs/ux/ux-structure.json`

## 1. Locked by UX (do not change without reopening the UX record)

| Screen | Primary action | Information priority (top 3) | Recovery that must stay visible |
|---|---|---|---|
| | | | |

Also locked: navigation model `<model>`, step count per flow, required states.

## 2. Principles that steer visual choices

Link [design principles](design-principles.md). Name the 1 or 2 that matter most visually.

## 3. Brand and context inputs

| Input | Value | Source (user / brand guide / HYPOTHESIS) |
|---|---|---|
| Brand attributes (3 adjectives) | | |
| Must use (logo, colour, font) | | |
| Must avoid | | |
| Usage context (light, motion, one hand, age range) | | |
| Accessibility floor | WCAG 2.2 AA contrast, text scaling to 200%, 44pt / 48dp targets | |
| Languages and longest strings | Vietnamese, real long labels | |

## 4. Open for exploration (where visual adds value)

- Type scale and density for <screen types>.
- Card vs list vs plain grouping for <screen>.
- Signature moment: <one place where delight is earned, e.g. success after moving a class>.
- Imagery role: identify / explain / brand moment / none.

## 5. Exploration rules

- Produce **2 materially different directions** on the same representative screen with the same content and state.
- Carry the chosen direction to 2 other screen types before full rollout.
- Record decisions (source, actual values, rejected option and why) in the delivery notes.

## 6. Short prompt (Claude Design)

```text
Keep the wireframe structure exactly. Screen: <name>, 390 wide.
Locked: primary "<label>", order <1,2,3>, recovery "<text>".
Brand: <3 adjectives>, colour <hex>, font <name>. Avoid <...>.
Make 2 clearly different directions (density, type scale, grouping). Same content, same state.
```

## 7. Review order

Comprehension and recovery → hierarchy → type and density → media → polish.
A beautiful direction that demotes the primary action or hides recovery fails review.
