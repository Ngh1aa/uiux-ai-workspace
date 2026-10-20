# Mobile: UX first, visual craft second

This is a resource of the existing visual-direction owner, not another orchestrator.
Use the mobile design contract and canonical decision JSON; do not create duplicate
state inventories. A runnable [specimen](../examples/mobile-care/index.html) illustrates
three different task compositions. It is synthetic, not a production app or evidence
of user preference.

## 1. Resolve the task before choosing a style

For each materially different screen, record:

| Entry state | User question | Essential information in order | Main action/destination | Feedback | Recovery |
|---|---|---|---|---|---|

Walk through overview → selection → form/review using actual content and existing
data rules. Include an empty result, invalid input and a recoverable failure.
State what the user sees and can do, not just which components exist.
Repair dead ends, misleading status, duplicate competing actions and lost input
before approving visual direction. Heuristic walkthroughs are not participant tests.

New mobile flow gates require an `ux` record on every declared page in the existing
v2 decision contract: `entry_state`, `user_goal`, `information_priority`,
`primary_action`, `destination`, `feedback`, `recovery`, `walkthrough_observation`,
`evidence_ref`, `review_source` (`agent-heuristic` or `human`) and `findings`.
Each finding records `observation`, `severity` (`blocker`, `major`, `minor`),
`status` (`open`, `resolved`) and `retest` when resolved. An open blocker or a
resolved finding without retest fails integrity. Existing contracts remain readable;
only gates with `ux_contract_required=true` demand the additional records.
The receipt says `RECORDED`, never “usability validated”: text records do not
authenticate the walkthrough or prove its conclusions. Current file binding is
rechecked at gate acceptance; claimed UX coverage cannot replace absent records.

Utility screens may share a familiar list. Do not force bento, asymmetry, a hero,
photos, or novelty into every form/settings screen. A list with consistent comparison
attributes is often better UX than varied cards.

## 2. Translate the task into composition

- Overview: current state and next useful action lead; secondary shortcuts follow.
- Selection/list: criteria, selected filters and comparable attributes lead.
- Form/review: step context, input, inline guidance/error and retained values lead.
- Record/status: state, accountable owner, identifier and next action stay together.
- Help: urgent path stays easy to find; everyday contact paths remain distinguishable.

For unresolved art direction, produce two materially different candidate compositions
on a representative screen with the same content/state. Compare real renders, not
prose names. Carry the chosen system to two other task types before broad rollout.
Honor explicit preservation and inherited-direction exceptions in the canonical v2
contract; do not generate alternatives for every state.

## 3. Specify the visual choices

Specify title/body/meta/action sizes, line heights, weight, gutters, grouping and
padding as semantic tokens. Test real Vietnamese and long labels. Keep the same
role consistent; a large decorative heading must not displace the next action.

Assign each card a role: selection, summary, action, content or status. Remove its
surface if spacing/dividers communicate the grouping better. Give whitespace a
purpose: grouping, reading, reachability or emphasis. Never fix emptiness by adding
unrelated text, fake metrics or arbitrary imagery.

Assign every image a job: identify a person/place, explain a process, preview content,
or provide a deliberate brand moment. Record source/license, crop, safe zone,
fallback and alt semantics. Stock imagery cannot imply an assigned doctor or a live
clinic. Missing assets require an honest illustration/fallback, not invented provenance.

An “iOS pastel” request leaves layout, density, typography and media decisions open.
Store approved captures plus their component source and reasons in the project.
They are reusable references, not model training or a promise of identical output.

## 4. Inspect rendered output

Open captures at narrow phone, ordinary phone and desktop browser presentation;
check enlarged text, keyboard/focus, safe areas and supported interaction states.
Review in order: comprehension/recovery → hierarchy → type/density → media → polish.
For every defect record screen/state/position, impact, owner, fix and same-state retest.
Use the existing seven-sign checklist, including “có mục đích rõ”; no blanket style ban.
Numeric averages cannot hide a blocking usability defect.

## Sources and limits (checked 2026-10-20)

- [NN/g heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/):
  status visibility, recognizable actions, consistent language and recovery underpin
  the walkthrough. These broad heuristics do not prescribe a palette or layout.
- [WCAG 2.1 contrast](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html):
  measure actual foreground/surface pairs; ordinary text 4.5:1, qualifying large text
  3:1. Gradient backgrounds require checking where the text actually appears.
- [Apple layout](https://developer.apple.com/design/human-interface-guidelines/layout)
  and [Material layout](https://m3.material.io/foundations/layout/understanding-layout/overview)
  remain platform references. Automated fetch could not inspect their full content
  in this upgrade; do not claim newly verified detailed rules from them.

Composition suggestions and specimen dimensions are professional hypotheses.
Rendered inspection can establish visible defects; human preference, clinical rules,
native runtime behavior and product impact need their own evidence.
