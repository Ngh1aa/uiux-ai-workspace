# Example: tutoring-centre app, "book a make-up class"

Synthetic example to show the shape of U1 to U6. All inputs are `HYPOTHESIS`;
no real participants took part. Names and numbers are `SAMPLE`.

## U1. Task model

| Rank | Task | Frequency × consequence |
|---|---|---|
| 1 | Book or move a class | Weekly × high (missed class = lost fee) |
| 2 | Check today's schedule and room | Daily × medium |
| 3 | See homework and teacher feedback | Weekly × medium |
| 4 | Pay tuition | Monthly × high |

JTBD (task 1):

```text
When my child is sick on class day, I want to move the class to another slot,
so I don't lose the session I already paid for.
Scenario: parent, Android phone, at work, 2 minutes between meetings, opened from a Zalo reminder.
Success signal: new slot confirmed, old slot released, teacher notified, calendar updated.
```

## U2. Flow (task 1)

```mermaid
flowchart TD
    E1([Zalo reminder: "Class at 17:30 today"]) --> S1[Class detail]
    E2([Cold open]) --> S0[Home: today's classes] --> S1
    S1 -->|"Can't attend"| S2[Choose reason: sick / busy / other]
    S2 --> S3[Pick make-up slot]
    S3 --> D1{Slot in same level?}
    D1 -->|Yes| S4[Review: old → new, policy note]
    D1 -->|None this week| R1[Show next week + "notify me if a slot opens"]
    R1 --> S3
    S4 -->|Confirm| D2{Server ok?}
    D2 -->|Yes| X([Moved. Teacher notified. Add to calendar])
    D2 -->|No| R2[Keep choice, explain, retry]
    R2 --> S4
```

Happy path: 4 screens, 2 taps of decision, 0 typed fields. Within budget.

## U3. Screen inventory (excerpt)

| Screen | Entry state | User question | Information priority | Primary action | Destination | Feedback | Recovery |
|---|---|---|---|---|---|---|---|
| Class detail | From reminder, class today | "Is it today, where, and can I change it?" | time + room, teacher, change option | "Can't attend" | Reason | none | If class already started: show "contact centre" with phone |
| Pick make-up slot | Reason chosen | "Which slot fits and is the same level?" | same-level slots by day, seats if < 5, policy | Select slot | Review | Selected state | No slot: R1 |
| Review | Slot chosen | "Am I sure, and what changes?" | old → new, make-up policy, fee (none) | "Confirm move" | Success | Pending spinner on button | Server error: R2 keeps choice |

## U4. Navigation

Tab bar with 4 items: Home, Schedule, Learning, Account.
Reason: tasks 1 to 3 are frequent peers; payment is monthly so it lives in Account
with a due badge on Home when payment is near. Booking is contextual from a class, not a tab.

## U5. Wireframe spec (Pick make-up slot)

1. Context: "Moving: English B1, Tue 17:30" (answers "am I moving the right class?")
2. Week switcher, current week default.
3. Slot list grouped by day; each row: time, teacher, room, "2 seats left" only when < 5.
4. Sticky "Continue", disabled with helper "Choose a slot" until selection.
5. Empty: "No B1 make-up slots this week" + "See next week" + "Notify me".

## U6. Walkthrough findings (agent-heuristic)

| # | Scenario | Screen / step | Finding | Severity | Fix | Retest |
|---|---|---|---|---|---|---|
| 1 | First-time parent from Zalo | Class detail | "Can't attend" read as cancel with no refund | major | Rename "Move this class", add helper "Free, keeps your session" | resolved, retested S1 |
| 2 | Payment-era user, slot taken | Review → confirm | Slot taken between pick and confirm, original flow returned to Home | blocker | R2 returns to slot list with message and keeps reason | resolved, retested S3 |
| 3 | Large text | Slot list | Teacher + room wrap, seats badge pushed off screen | minor | Stack row on 2 lines | open (handled in visual stage) |

Verdict: `READY_WITH_RISKS`. Hypotheses to validate: wording of "Move this class"; whether parents expect teacher choice. Next step: 5 moderated sessions with parents on task 1 and 4.
