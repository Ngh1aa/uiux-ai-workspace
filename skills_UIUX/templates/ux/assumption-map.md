# Assumption map

Plot each assumption by **importance** (if wrong, does the plan fail?) and **evidence** (how much do we know?).
Test the top-left quadrant first: high importance, low evidence.

| # | Assumption | Type | Importance (1-5) | Evidence (1-5) | Quadrant | Test method | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| A1 | Parents will reschedule in the app instead of calling | Desirability | 5 | 1 | TEST FIRST | 5 moderated sessions on prototype | | open |
| A2 | | Viability | | | | | | |
| A3 | | Feasibility | | | | | | |
| A4 | | Usability | | | | | | |

Types: Desirability (do they want it), Viability (does it pay), Feasibility (can we build it),
Usability (can they use it), Ethics/Trust (should we, will they trust it).

```text
            High importance
                 │
   TEST FIRST    │   MONITOR / BUILD ON
  (low evidence) │   (high evidence)
─────────────────┼──────────────────────
   PARK          │   SAFE
                 │
            Low importance
```

Rules: one assumption per row; write it so it can be proven wrong; update Evidence after each test, do not delete rows.
