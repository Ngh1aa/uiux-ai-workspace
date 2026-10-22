---
name: moderated-usability-testing
description: Design and run moderated usability tests for prototypes or live experiences using realistic tasks, neutral facilitation and observable success criteria. Use when validating comprehension, navigation, forms, flows or redesign quality.
---

# Moderated Usability Testing

## Workflow

1. Define research questions and risky journeys (start from the assumption map: high importance, low evidence).
2. Create realistic tasks with a goal but no navigation hints.
3. Prepare moderator guide, warm-up, think-aloud prompts and neutral probes.
4. Define success, partial success, failure and critical-error criteria.
5. Pilot once (colleague) to fix broken tasks and prototype gaps.
6. Observe behavior, errors, workarounds and recovery; separate observation from interpretation.
7. Debrief after each session and synthesize across sessions.
8. Rank issues by evidence, severity and journey impact.

Use the [usability test plan template](../templates/ux/usability-test-plan.md).

## Writing tasks

| Bad (leads) | Good (goal only) |
|---|---|
| "Click Schedule and reschedule Tuesday's class." | "Your child is sick today. Make sure the lesson isn't wasted." |
| "Find the Pricing page." | "Your friend asked how much a term costs. Find out." |

Use words from the user's world, not UI labels. Give realistic data (names, dates, amounts).

## Neutral probes

"What are you looking for?" · "What do you expect will happen?" · "What would you do now if I weren't here?" · "Tell me more about that."
Avoid: "Did you see the button?", "Was that easy?", "Do you like it?"

## Sample size, honestly

Around 5 participants per distinct segment usually reveals the most frequent major problems in a qualitative round. It is not a statistical sample; do not report percentages from it. Run another round after fixes rather than more sessions in one round.

## Remote and Vietnam-context notes

- Zalo/Google Meet with screen share works; ask for phone screen mirroring for mobile tests.
- Confirm consent for recording in the participant's language.
- Compensation and time window stated up front; avoid testing during work hours for working parents unless they choose it.

## Rules

- Do not teach the interface during the task.
- Do not ask users whether they "like" a flow as a substitute for observing success.
- Give assistance only after capturing the failure point.
- Test realistic content whenever comprehension matters.
- Never merge these findings with `agent-heuristic` walkthroughs; keep evidence classes separate.

## Output

Test plan, task script, observation notes, task outcomes, severity-ranked findings and next experiments.

## Quality gate

- Tasks do not reveal the answer.
- Findings cite observed behavior with session IDs.
- Critical issues map to actionable changes or follow-up research.
- No invented quotes, counts or percentages.

## Baseline

GOV.UK moderated usability-testing guidance; NN/g guidance on think-aloud and task writing. Usability metrics may be combined with qualitative findings when useful.
