# Reference-Aware Visual QA

This contract defines how UIUX Factory may use reference screenshots after implementation.

## Core rule

A reference is evidence, not permission to clone.

Reference similarity is interpreted through the frozen `spec_profile`; Visual QA must not reclassify the task after implementation.

## Profile policy

| Profile | Comparison policy | Blocking behavior |
|---|---|---|
| `pixel_faithful` | strict same-viewport reference comparison plus semantic/human review | measured mismatch or missing comparable reference evidence blocks PASS |
| `preserve_and_extend` | strict only for explicitly protected visual surfaces; whole-page comparison is advisory | whole-page visual distance must not block new/extended work |
| `redesign` | no old-reference pixel-similarity success criterion | reference visual distance is `N/A_JUSTIFIED`; frozen new art direction/spec owns acceptance |
| `original_design` | spec-only visual acceptance | reference pixel comparison is `N/A_JUSTIFIED` |

## Pixel-faithful measurements

When an authoritative `existing_website` capture and target screenshot exist at the same viewport, the deterministic evaluator records:

- source and target screenshot paths + SHA-256;
- normalized mean absolute RGB difference (`normalized_mae`);
- ratio of pixels whose largest channel delta exceeds a bounded tolerance;
- the active threshold values;
- PASS/FAIL/CANT_TELL.

Current v1 thresholds are intentionally explicit implementation defaults:

```text
normalized_mae <= 0.08
pixels above per-channel tolerance <= 0.20
per-channel tolerance = 24 / 255
```

These thresholds are machine heuristics for browser-output drift, not a claim of perceptual identity. Semantic screenshot review and human visual review remain separate gates.

Do not relax thresholds merely because an implementation fails. If the threshold itself is unsuitable for a known browser/rendering environment, change it through an explicit contract revision with benchmark evidence.

## Authoritative reference role

Strict reference comparison uses captures whose role is `existing_website`.

Ordinary inspiration/reference URLs are never silently promoted into clone targets.

For `pixel_faithful`, absence of a comparable authoritative reference capture produces `cantTell` and blocks fidelity PASS rather than inventing evidence.

## Preserve-and-extend

Whole-page pixel similarity is unsafe for extension work because correct new sections naturally make the page different.

Strict visual comparison is allowed only when the frozen spec explicitly marks a surface as pixel/visual exact, for example through a future structured surface marker or a P0 exact-preservation contract.

Until a target-side per-selector crop can be measured, whole-page metrics remain supporting/advisory evidence and cannot reject an otherwise valid extension.

Behavior/API/data preservation continue to use their own contracts; do not substitute screenshot similarity for those checks.

## Redesign

For redesign work:

- preserve product/data/journey truth where the frozen spec requires it;
- evaluate the new rendered UI against the approved art direction, page roles, responsive behavior and QA contract;
- never treat "looks different from the old UI" as a defect by itself.

## Original design

No visual reference fidelity obligation exists unless the user explicitly changes the task/profile. Use frozen spec + BrowserQA + VisualCritic + human review.

## Quality-loop ownership

The quality loop runs:

```text
BrowserQA
→ ReferenceAwareVisualQA
→ VisualCritic
→ evidence contract
→ repair / re-render
```

For strict pixel-faithful mismatch, the measured failure is injected as an actionable visual issue so repair targets the earliest owning layout/typography/media/motion rule.

For strict `cantTell` (for example missing authoritative reference screenshot), repairing CSS cannot manufacture evidence. The run blocks and reports the missing evidence instead.

## Non-negotiables

- Do not infer clone intent merely from the presence of a URL.
- Do not make whole-page pixel similarity a redesign/original-design score.
- Do not call screenshot metrics semantic or UX correctness.
- Do not call missing comparison evidence PASS.
- Do not let aggregate visual polish overrule a strict `pixel_faithful` failure.
- Do not weaken the gate to obtain green CI.
