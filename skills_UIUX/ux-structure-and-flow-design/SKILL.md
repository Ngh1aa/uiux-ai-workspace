---
name: ux-structure-and-flow-design
description: Owns the UX structure layer between research and visual design. Turns top tasks and JTBD into user flows, task flows, a screen/state inventory, navigation model, low-fidelity wireframe spec and a scenario walkthrough, then issues the UX Readiness verdict that unlocks visual direction. Use for any new product, page set, app or redesign before choosing style, palette or components.
---

# UX Structure & Flow Design

## Goal

Decide **what the experience does and in what order** before deciding **what it looks like**.
The output is a structure a visual designer can dress without having to guess
the task, the next action, the feedback or the way back from failure.

This skill does not replace the research owners or the visual owner. It sits between them:

```text
product-discovery / audience-intent-and-top-tasks / ux-research-and-journey   (WHY + WHO)
        ↓
ux-structure-and-flow-design                                                  (WHAT + ORDER)
        ↓  UX Readiness = READY
visual-design-direction / design-system-and-components                        (HOW IT LOOKS)
```

**Prerequisites.** Minimum inputs (link them, do not copy them):

- a problem statement with an outcome metric or an explicit `UNKNOWN`;
- 1 to 3 primary audiences or proto-personas labelled `EVIDENCED` or `HYPOTHESIS`;
- a ranked top-task list.

If any is missing, produce a thin version from the [templates](../templates/ux/README.md),
label it `HYPOTHESIS`, and continue. Do not stall the work; do not upgrade the label later without evidence.

## Workflow (U1 to U6)

**U1. Task model**

For each top task write one JTBD line and one concrete scenario:

```text
When <situation>, I want to <motivation>, so I can <expected outcome>.
Scenario: <who> on <device/context> with <constraint, e.g. 3 minutes on a bus, weak 4G>.
Success signal: <observable end state>.
```

Rank tasks by frequency × consequence. Only the top 3 to 5 tasks drive structure;
everything else must fit around them, not compete with them.

**U2. Flows**

For every top task draw a **user flow** (screens + decisions) in Mermaid, including:

- the happy path;
- at least one alternative path (returning user, different entry point);
- at least one failure path (invalid input, empty result, network or permission failure)
  that ends in recovery, never in a dead end.

Add a **task flow** (step list) where a single screen holds several actions.
Count steps and decisions on the happy path; if a top task needs more than ~7 steps,
record why or simplify. Read [flow practice](references/ux-structure-practice.md#flows) for notation.

**U3. Screen and state inventory**

One row per materially different screen. Use the same field names as the canonical
`pages[].ux` record in `visual-design-direction` so work is not duplicated:

| Screen | Entry state | User question | Information priority (ordered) | Primary action | Destination | Feedback | Recovery |
|---|---|---|---|---|---|---|---|

Then list required states per screen (default, loading, empty first-use, empty filtered,
error, partial, success, offline, permission). Route deep state work to
`state-feedback-and-error-recovery`.

**U4. Navigation and IA model**

Choose the navigation model from the task model, not from habit:

| Signal | Usual model |
|---|---|
| 3 to 5 peer destinations used daily | Tab bar (mobile) / persistent top nav (web) |
| One dominant task, others rare | Hub with one primary action + secondary menu |
| Linear high-stakes task | Wizard / stepper, no global nav during the task |
| Large content set | Hierarchy + search + filters |

Produce a sitemap or screen map. Labels use the user's words (from research or the task model),
not internal team names. For large or contested IA, route `information-architecture`
and validate with `card-sorting-and-tree-testing`.

**U5. Low-fidelity wireframe spec**

Per key screen, specify content blocks **in priority order** with purpose and behaviour, no styling:

```text
Screen: Class booking / Select time
1. Context bar: selected class + teacher (answers "am I booking the right thing?")
2. Date strip: next 14 days, unavailable days visibly disabled with reason on tap
3. Time slots: grouped morning/afternoon/evening, seats left shown only when < 5
4. Primary action: "Continue" sticky, disabled until a slot is chosen, with helper text why
5. Recovery: no slots → suggest nearest date + "notify me" option
```

Optional: a greyscale HTML or Claude Design wireframe. Keep it greyscale, one typeface,
no brand colour, so reviewers judge structure, not taste.

**U6. Walkthrough and UX Readiness verdict**

Run the wireframes against **5 scenario-based expert walkthroughs** (AGENTS.md §12):
different goal, confidence, device and interruption per scenario. Record each finding with
screen, step, severity (`blocker` / `major` / `minor`), fix and retest.
Then complete the [UX Readiness gate](checklists/ux-readiness-gate.md).

Verdicts:

- `READY`: no open blocker; every top task has happy + failure path; every key screen has a primary action and recovery.
- `READY_WITH_RISKS`: no blocker, but named majors or `HYPOTHESIS` inputs remain; list them for validation.
- `NOT_READY`: an open blocker or a top task without a complete flow. Visual direction must not start.

A walkthrough by the agent is `agent-heuristic` evidence, never participant research.

## Outputs and resources

Write under the target project (or the closest existing docs folder):

```text
docs/ux/task-model.md            U1
docs/ux/flows.md                 U2 (Mermaid)
docs/ux/screen-inventory.md      U3
docs/ux/navigation-model.md      U4
docs/ux/wireframe-spec.md        U5
docs/ux/ux-readiness.md          U6 verdict + findings
```

Small tasks (one page, one flow) may combine these into one `docs/ux/ux-structure.md`.

**Machine-checkable record.** For gated flows also write `docs/ux/ux-structure.json`
(schema: `python -B skills_UIUX/ux-structure-and-flow-design/scripts/check-ux-structure.py --schema`)
and run the checker with `--root <project>`. It fails on: a top task without a flow, a flow
without a failure path, a flow over the step budget without a reason, fewer than 5 walkthrough
scenarios or none exercising failure, a resolved finding without retest, a verdict that
contradicts open blockers/majors or HYPOTHESIS inputs, and a top task hidden in navigation.
PASS means `READY` or `READY_WITH_RISKS` with consistent records; usability stays `UNKNOWN`.
After PASS, `--export-page-ux <evidence_ref>` emits `pages[].ux` blocks for the
visual-design-direction v2 contract so the visual stage reuses, not retypes, the UX record.

**Resource routing**

- Need artifact shapes? Use [UX templates](../templates/ux/README.md).
- Handing to visual design? Fill [visual brief](../templates/ux/visual-brief.md) and [design principles](../templates/ux/design-principles.md).
- Need a machine-checked example or a greyscale wireframe pattern? See [example record](examples/edtech-class-booking/docs/ux/ux-structure.json) and [wireframes](examples/edtech-class-booking/wireframes.html).
- Unsure which UX skill owns a decision? Read [UX skill map](../../docs/UX-SKILL-MAP.md).
- Need flow notation, step budgets, navigation trade-offs or wireframe rules? Read [practice](references/ux-structure-practice.md).
- Before handing to visual design, run [UX Readiness gate](checklists/ux-readiness-gate.md).
- Need a worked example? Read [edtech booking example](examples/edtech-class-booking.md).
- Forms with branches or save/resume → `complex-forms-and-wizards`.
- Feedback and failure states → `state-feedback-and-error-recovery`.
- Copy that changes comprehension → `ux-writing-and-microcopy`.
- AI features (generation, suggestions, agents) → `human-ai-interaction-design`.

## Acceptance criteria

- Every top task traces: JTBD → flow → screens → primary action → success signal.
- Every flow has at least one failure path ending in recovery.
- Every key screen answers one user question first and has one primary action.
- Navigation model is justified by task frequency, not copied from a reference.
- Walkthrough findings have severity, fix and retest; no open blocker at `READY`.
- Labels on evidence are honest: `EVIDENCED`, `HYPOTHESIS`, `UNKNOWN`.

**Anti-patterns**

- Choosing a palette, font or "vibe" before U3 exists.
- Wireframes that are already high-fidelity mockups (they hide structural problems behind polish).
- Flows that only show the happy path.
- Two equal primary buttons on one screen without a reason.
- Navigation named after the org chart.
- Writing invented user quotes into personas or findings.
- Treating `READY` as proof of usability; it only means structure is complete enough to design on.
