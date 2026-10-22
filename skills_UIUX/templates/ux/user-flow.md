# User flow: <top task name>

**Job:** J#
**Entry points:** cold open / deep link / notification / search / shared link / return after interruption
**Success signal:**

## Flow

```mermaid
flowchart TD
    E([Entry]) --> S1[Screen 1]
    S1 -->|user action| S2[Screen 2]
    S2 --> D1{Decision or system check}
    D1 -->|ok| S3[Screen 3]
    D1 -->|fail| R1[Recovery: what the user can do next]
    R1 --> S2
    S3 --> X([Success state])
```

Notation: `([ ])` entry/end, `[ ]` screen, `{ }` decision, `R#` recovery node.

## Path inventory

| Path | Covered? | Ends in |
|---|---|---|
| Happy path | yes / no | success |
| Alternative (returning user / other entry) | | |
| Failure: invalid input | | recovery R# |
| Failure: empty / no result | | recovery R# |
| Failure: network / permission / timeout | | recovery R# |

## Step budget

Screens: __ Decisions: __ Typed fields: __
Over budget? Reason or simplification:

## Open questions

-
