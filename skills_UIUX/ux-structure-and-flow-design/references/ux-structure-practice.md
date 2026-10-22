# UX structure practice

Load only the section the current decision needs.

## Flows

### Notation (Mermaid)

```mermaid
flowchart TD
    E([Entry: push reminder]) --> S1[Home: next class card]
    S1 -->|Tap "Book again"| S2[Select time]
    S2 --> D1{Slot available?}
    D1 -->|Yes| S3[Review + pay]
    D1 -->|No| R1[Suggest nearest date / notify me]
    R1 --> S2
    S3 --> D2{Payment ok?}
    D2 -->|Yes| X([Success: booked, added to calendar])
    D2 -->|No| R2[Keep selection, show reason, retry or other method]
    R2 --> S3
```

Conventions:

- `([ ])` entry and end states; `[ ]` screens; `{ }` decisions made by user or system.
- Name recovery nodes `R1, R2...` so findings can cite them.
- Label edges with the user's action in their words, not component names.
- One flow per top task. Do not merge tasks into a single mega-diagram.

### Step budget

Count on the happy path: screens visited, decisions, fields typed.
Rough review triggers, not hard rules:

| Task type | Review when more than |
|---|---|
| Daily repeat task (check status, rebook) | 3 screens or 1 typed field |
| First-time setup / onboarding | 5 screens, or any question that is not needed now |
| High-stakes transaction (payment, application) | 7 steps without a progress indicator or review step |

When over budget, try in order: remove the step, pre-fill from known data,
defer to later, merge with an adjacent step, then accept with written reason.

### Entry points

List every realistic entry: cold open, deep link, notification, search result,
shared link, returning after interruption. A flow that only works from the home screen
fails real usage. Each entry must land the user with enough context to know where they are.

## Screen and state inventory

### Writing a good "user question"

The user question is what the person needs answered **on arrival**, in their words.

| Weak | Strong |
|---|---|
| "Dashboard" | "Is anything due today that I'll miss?" |
| "Course detail" | "Is this course right for my child's level, and when does it start?" |
| "Settings" | "How do I stop these notifications?" |

Information priority then follows the answer: what answers the question first, what
supports the decision second, what is reference only last.

### Minimum states

| Situation | Must specify |
|---|---|
| Lists / search | first-use empty, filtered empty, loading, partial load, error |
| Forms | inline error, summary error, submitting, server error with input kept, success |
| Async actions | pending, success, failure, retry, cancel if long |
| Account / permission | signed out, no permission, expired session with return path |
| Mobile | offline, slow network, interrupted by call/app switch |

## Navigation model

| Model | Use when | Watch out for |
|---|---|---|
| Tab bar / top nav | 3 to 5 peer destinations, frequent switching | More than 5 items; hiding the main task in "More" |
| Hub + primary action | One dominant job (book, create, scan) | Burying secondary but critical tasks |
| Stepper / wizard | Linear, consequential task | Losing input on back; no save/resume for long tasks |
| Hierarchy + search | Large catalogue or content | Labels that only insiders understand |
| Contextual (inline) | Actions belong to a specific object | Discoverability; provide a visible affordance |

Decide what stays persistent, what is contextual and what is hidden. Hidden must be rare tasks only.

## Wireframe spec rules

1. Greyscale, one typeface, real content (real Vietnamese strings, real lengths). Lorem ipsum hides problems.
2. Each block has a purpose line: which user question it answers.
3. One primary action per screen. Secondary actions are visibly weaker.
4. Specify behaviour, not pixels: what happens on tap, empty, error, long text.
5. Mark fake data `SAMPLE` so nobody mistakes it for a product decision.
6. Mobile first when mobile is a primary context; desktop is an expansion, not a squeeze.
7. Thumb zone: frequent actions within reach on phone; destructive actions not next to primary.

## Walkthrough method (5 scenarios)

Pick scenarios that stress different things:

| # | Vary | Example |
|---|---|---|
| 1 | First-time, low confidence | Parent opens app from a Zalo link, never used it |
| 2 | Returning, in a hurry | Student rebooking between classes, one hand |
| 3 | Failure path | Payment declined, slot taken while paying |
| 4 | Accessibility / situational | Large text setting, bright sunlight, weak 4G |
| 5 | Edge content | Long name, 0 results, 300 results, expired item |

For each step ask, in this order:

1. Does the user know where they are and what this screen is for?
2. Is the next action obvious and reachable?
3. After acting, does feedback confirm what happened?
4. If something fails, is there a way forward that keeps their work?
5. Is anything asked or shown that this user does not need now?

Severity:

- `blocker`: task cannot be completed, or data/money/trust is lost.
- `major`: task completes with significant confusion, error or delay.
- `minor`: friction or inconsistency that does not change outcome.

## Handoff to visual design

Hand over: task model, flows, inventory, navigation model, wireframe spec, readiness verdict.
The visual designer may change layout expression and hierarchy styling, but must not
remove a recovery path, demote the primary action, or reorder information priority
without reopening the UX record and noting why.

## Sources

- Nielsen Norman Group, usability heuristics and task analysis articles.
- GOV.UK Service Manual, design and research guidance (one thing per page, start with user needs).
- Clayton Christensen et al., Jobs to Be Done framing.
- Apple HIG and Material Design navigation guidance for platform patterns.

Verify current versions of platform guidance before quoting specific thresholds.
