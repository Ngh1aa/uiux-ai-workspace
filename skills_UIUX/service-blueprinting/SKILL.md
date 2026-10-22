---
name: service-blueprinting
description: Map end-to-end experience across user actions, frontstage touchpoints, backstage processes, systems and handoffs. Use when a website flow depends on support, operations, approvals, offline steps or multiple teams.
---

# Service Blueprinting

## Goal and scope

Make the whole service visible, from what the user does to the people, processes and systems that make it work, so the team can tell which problems the interface can fix and which need operational change. A good blueprint ends arguments of the form "the website is confusing" by showing that step 4 waits three days for a manual approval nobody owns.

**When not to use**

- Mapping only user goals, emotions and touchpoints with no backstage: use `ux-research-and-journey`.
- Keeping continuity across email, phone, staff and locations once the service is understood: use `omnichannel-experience-continuity`.
- Defining service-level outcome metrics and health loops: use `journey-outcome-and-service-health`.
- Translating a physical service ritual into a digital journey: use `service-experience-to-digital-journey`.
- Designing in-product progress for a long-running process: use `complex-workflow-and-progress-ux`.

**Prerequisites**

- A named service and one primary scenario (persona plus goal), not "all users".
- Access to at least one person who does the backstage work, plus any process docs, SLAs, ticket data or logs.
- Agreement on whether the blueprint is current state (as-is) or future state (to-be). Never both on one canvas.

## Decisions

**Scope and grain.** One blueprint per scenario. Set the start trigger and the end state the user cares about (e.g. "money in account", not "form submitted"). If a step expands into more than a handful of backstage actions, link a sub-blueprint instead of crowding the main one.

**Lanes, top to bottom.** Use the standard structure (Shostack; Bitner, Ostrom and Morgan; NN/g):
1. Physical and digital evidence: what the user sees or holds at each step (email, screen, receipt, letter, SMS).
2. Customer actions.
3. Line of interaction.
4. Frontstage actions: staff or system actions the user directly experiences.
5. Line of visibility.
6. Backstage actions: staff work the user does not see.
7. Line of internal interaction.
8. Support processes and systems: internal teams, vendors, databases, queues, third parties.

A step crossing the line of interaction is a touchpoint; crossing the line of visibility is where the user's view ends and trust starts depending on communication.

**Evidence lane is mandatory.** For every customer action, record the artifact that tells the user what happened. A blank evidence cell after a user action is a finding: the user is left without proof or status.

**Fail points.** Mark any step where the service can break: handoff between teams, manual data re-entry, eligibility checks, third-party calls, document review. For each, record failure mode, detection (who notices, how), and recovery path. If nobody detects it until the user complains, flag it as a priority.

**Wait points.** Mark every wait the user experiences, with actual duration from data where possible (range, not ideal SLA) and what the user is told during the wait. A wait longer than the user's expectation with no evidence artifact is the most common root cause of "where is my order" contacts.

**Swimlane ownership.** Every backstage and support action names an owning role or team, not "ops". Every handoff names both sender and receiver. A handoff with no named receiver is an ownership gap and goes to the top of the opportunity list.

**UI or service problem.** Classify each pain point:
- UI: user cannot find, understand or complete something that the service would otherwise deliver.
- Service: the process itself is slow, fails, or needs information the user cannot reasonably give.
- Policy: rules or regulation create the friction.
Only UI problems are fixed by redesign alone. Service and policy problems may need interim UI (status, expectations) but must be logged with an operational owner.

**Evidence quality.** Tag each cell as observed, reported by staff, from data, or assumed. Assumed cells become research questions.

## Workflow

1. Define service outcome and start and end boundaries, scenario, and as-is or to-be.
2. Map user actions across digital and relevant offline channels (phone, branch, mail, in person).
3. Add frontstage interactions and support touchpoints, plus the evidence artifact for each step.
4. Add backstage people, processes, systems and data dependencies, with owners on every lane item.
5. Mark handoffs, waits, failure points and ownership gaps, with durations and detection paths.
6. Separate UI problems from service and operational problems (and policy).
7. Prioritize opportunities by user and operational impact, and list evidence gaps needing research.

**Anti-patterns**

- A journey map labelled "blueprint": no backstage lanes, no systems, no owners.
- Mapping the documented process instead of what staff actually do; workarounds (spreadsheets, side chats) are missing.
- Waits shown as SLA targets rather than observed ranges.
- Redesigning the form to "reduce drop-off" when users drop because a back-office check takes days and nobody tells them.
- "System" as an owner. Systems are tools; a role owns the outcome.
- Mixing as-is and to-be on one canvas, so nobody knows what is real.
- Blueprint made in a workshop without anyone from operations or support.
- Status page invented in the UI that the backstage cannot actually update.

**Resources**

- Need lane definitions, notation, cell templates or a filled example? Read [blueprint notation reference](references/blueprint-notation.md).
- Before handing off a blueprint, run [blueprint gate](checklists/blueprint-gate.md).

**Output**

1. Blueprint canvas (or table) with the eight lanes and step columns.
2. Step table:

| Step | Evidence | Customer action | Frontstage (owner) | Backstage (owner) | Support systems (owner) | Wait (observed) | Fail point and detection | Problem type | Evidence quality |
|---|---|---|---|---|---|---|---|---|---|

3. Ownership gap list: handoff, sender, missing receiver, proposed owner.
4. Opportunity backlog: pain point, problem type, user impact, operational impact, owner, interim UI mitigation.
5. Research gaps: assumed cells and how to verify them.

## Quality gate

- PASS only if every critical handoff names a sending and a receiving owner (critical handoffs have ownership).
- PASS only if offline and support steps in the scenario appear on the blueprint (offline and support steps are not ignored).
- PASS only if every user action has an evidence entry, or the gap is logged as a finding.
- PASS only if every wait has an observed duration or is tagged assumed.
- PASS only if every fail point lists detection and recovery.
- FAIL if a UI change is proposed to hide or disguise a broken backstage process without an operational owner logged (UI is not used to disguise a broken backstage process).
- PASS only if the blueprint identifies evidence gaps that need research (assumed cells listed with a verification method).

**Baseline and sources**

- G. Lynn Shostack, "Designing Services That Deliver" (Harvard Business Review, 1984), origin of blueprinting and fail points.
- Bitner, Ostrom and Morgan, "Service Blueprinting: A Practical Technique for Service Innovation" (lanes and lines).
- NN/g service blueprint guidance (evidence, lines of interaction, visibility, internal interaction).
- Stickdorn and colleagues, This Is Service Design Doing (workshop and research practice).
