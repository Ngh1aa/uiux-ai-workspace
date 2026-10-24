# Quality bar rubric

A scoring rubric for expert design review at the level expected by product design teams at large
technology companies. Use it on **rendered** output (screenshots or live UI), never on code or a
description alone. It is an expert heuristic: it improves work before handoff, but a score is not
evidence of user preference or task success. Record scores as `agent-heuristic` or
`expert-review`, never as user research.

## How to use

1. Render every screen in scope at the required sizes, both themes when supported, and the key
   states (default, empty, loading, error, long content, largest text size).
2. Check **hard fails** first. Any hard fail = the work is not ready, regardless of scores.
3. Score each dimension 1–5 using the anchors. Write one observation per score below 4, with the
   screen and element.
4. Fix, re-render, re-score. Do not raise a score without a new render.

## Hard fails

| # | Hard fail |
|---|---|
| HF-1 | Text or meaningful icon below WCAG AA contrast (4.5:1 text, 3:1 large text/UI) in any supported theme |
| HF-2 | Touch target below platform minimum (44 pt iOS, 48 dp Android, 24 px web) for a primary or frequent action |
| HF-3 | Content clipped, overlapping or overflowing horizontally at any required size or text scale |
| HF-4 | No visible focus indicator, or keyboard/screen-reader path blocked for the primary task |
| HF-5 | A required state (error, empty, loading) is missing for a data-driven screen |
| HF-6 | Status or required information conveyed by colour alone |
| HF-7 | Platform convention broken without reason (iOS edge-swipe back blocked, Android back ignored, browser back breaks the flow) |
| HF-8 | Two or more competing primary (filled) actions in the same region |
| HF-9 | Deceptive pattern (hidden cost, confirmshaming, pre-selected upsell, obstructed cancel) |
| HF-10 | Fabricated evidence in the design (fake reviews, invented metrics, unlabeled placeholder data presented as real) |

## Dimensions and anchors

| Dimension | 1 — not acceptable | 3 — competent | 5 — top-tier |
|---|---|---|---|
| **1. Task clarity** | Unclear what the screen is for or what to do next | Purpose clear after reading; primary action findable | Purpose and next action obvious in < 3 s; the screen anticipates the user's next question |
| **2. Hierarchy** | Everything competes; no focal point | One focal point, secondary content quieter | Clear 3-level reading order; scale, weight, colour and space all agree |
| **3. Layout & spacing** | Random gaps, misalignments | Consistent scale, aligned edges | Rhythm encodes structure (inner < outer gaps), optical alignment, nothing arbitrary |
| **4. Typography** | Many sizes/weights, poor measure, clipped diacritics | On a scale, readable, correct line heights | Expressive yet disciplined ramp, perfect measure, tabular numbers, scales with accessibility sizes |
| **5. Colour & contrast** | Colours without roles, contrast issues | Role-based palette, AA met | Restrained, brand-led accent used only where it means something; flawless in both themes |
| **6. Components & consistency** | Same thing looks different across screens | Shared components, consistent states | System-level coherence; every component has full state coverage and feels of one family |
| **7. Interaction & feedback** | Taps with no response, unclear states | Every action has feedback; errors explain | Feedback is immediate, proportional and reversible (Undo); motion explains space |
| **8. Content & microcopy** | Jargon, vague labels, blame in errors | Clear, consistent, sentence-case labels | Copy is concise, human and specific; empty and error states help the user move forward |
| **9. Platform fit & responsiveness** | Desktop UI shrunk to mobile; non-native patterns | Adapts per breakpoint/platform | Feels native on each platform and size class while keeping one brand |
| **10. Craft & distinctiveness** | Generic template look, visual noise | Clean and professional | Memorable signature details that serve the brand and the task; nothing decorative without purpose |

Accessibility is not a separate score: it is enforced through the hard fails and is part of
dimensions 4, 5, 7 and 9.

## Thresholds by task size (see `WORKFLOWS.md`)

| Size | Requirement |
|---|---|
| XS | No hard fail on affected screens |
| S | No hard fail; relevant dimensions ≥ 3 |
| M | No hard fail; average ≥ 3.5; no dimension < 3 |
| L | No hard fail; average ≥ 4.0; no dimension < 3.5 |
| XL | As L, plus design-system validation passes and dimension 6 ≥ 4 |

Averages never hide a failure: one dimension below its floor fails the gate.

## Three-round critique (L and XL)

1. **Self-review** against this rubric and the [craft standards polish pass](../../ui-craft-and-visual-qa/references/craft-standards.md#11-the-polish-pass-do-this-last-every-time).
2. **Role-based review**: review the same renders three times, once each as (a) a first-time user
   on a small phone, (b) an accessibility reviewer (large text, screen reader order, contrast),
   (c) a design-system owner (consistency, tokens, components). Record findings by role.
3. **Cold review**: show only the screenshots, without the brief, and ask: what is this screen for,
   what would you tap first, what feels off? Compare the answers with the intended purpose.

With a human reviewer available, round 3 should be done by a person outside the work and recorded
as `expert-review`; otherwise label it `agent-heuristic`. The author never runs round 3: hand it to a
fresh reviewer with the [cold review brief](cold-review-prompt.md).

## Score record template

```text
Screen / state:            <name, size, theme>
Hard fails:                none | HF-n: <observation>
Scores:                    1:_ 2:_ 3:_ 4:_ 5:_ 6:_ 7:_ 8:_ 9:_ 10:_   avg: _
Below-4 observations:      <dimension> — <screen/element> — <fix>
Evidence:                  <capture file + digest>
Reviewer class:            agent-heuristic | expert-review
```
