---
name: visual-taste-calibration
description: Calibrates an existing visual direction or implemented UI for distinctiveness, subject-matter fit and anti-template quality without replacing visual-design-direction. Use when a design is coherent but still feels generic, AI-templated, visually interchangeable, over-decorated or insufficiently specific to the brief.
---

# Visual Taste Calibration

## Boundary

This is a **calibration adapter**, not a visual-design orchestrator.

Use `visual-design-direction` to create the project's layout/type/color/media/motion grammar. Use this skill afterward when the active question is: **does the direction feel intentionally specific, or did it fall back to familiar generated/template defaults?**

Source precedence remains:

`user request → project truth → passed Design Contract → local visual direction → this calibration → generic prior`

## Workflow

1. Read project truth, current Design Contract/visual direction and representative content.
2. Identify the project's real subject matter, audience, decision objects, media reality and brand/domain cues.
3. Inspect the proposed direction or rendered UI for interchangeable defaults.
4. Identify one primary memorable commitment worth preserving or strengthening.
5. Challenge typography, structural devices, composition and motion against actual content meaning.
6. Produce `KEEP / REVISE / REMOVE` recommendations; do not redesign the whole project from scratch.
7. Hand material revisions back to `visual-design-direction` / Design Contract owner.
8. Verify on representative page roles or rendered screenshots when available.

## Calibration questions

- Could this UI be repurposed for an unrelated industry by swapping logo/copy?
- Is the main visual idea traceable to subject matter, audience or brand truth?
- Are numbered labels, dividers, badges, arrows and decorative structure carrying information?
- Is typography chosen deliberately for this content/locale or from habit?
- Is the design trying to be memorable in too many places at once?
- Is motion explaining hierarchy/state, or merely repeating generic reveal patterns?
- Do materially different page roles still look interchangeable?

## Output

For substantial work, add a short section to `docs/visual-direction.md` or the Design Contract:

```text
Visual taste calibration
- Memorable commitment:
- Generic tells found:
- KEEP:
- REVISE:
- REMOVE:
- Representative verification:
```

## Hard rules

- Do not use novelty as a quality score.
- Do not reject a common pattern when project truth makes it the right pattern.
- Do not override accessibility, content clarity, interaction predictability or established brand rules to appear distinctive.
- Do not create a second visual direction in parallel with the Design Contract.
- A font/color swap alone is not substantial distinctiveness.

## Progressive reference

Read [references/visual-taste-calibration.md](references/visual-taste-calibration.md) when a deeper anti-generic critique is needed. It is an adapted synthesis of Anthropic Frontend Design pinned in `vendor/external-uiux/SOURCE-LOCKS.md`.

## Acceptance criteria

- Recommendations are traceable to this project's subject matter/brand/content.
- At least one generic/interchangeable pattern is explicitly challenged when present.
- Boldness is concentrated rather than scattered.
- Material changes return to the canonical Design Contract/visual-direction owner.
- Rendered evidence is used when claiming the implemented UI is materially less generic.
