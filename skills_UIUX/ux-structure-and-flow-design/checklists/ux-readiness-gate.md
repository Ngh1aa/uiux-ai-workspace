# UX Readiness gate

Run before any visual direction, palette, typography or component styling work.
Every item is PASS / FAIL / N/A with a one-line reason. N/A needs a reason too.

## A. Inputs (labels must be honest)

- [ ] Problem statement exists with an outcome metric or explicit `UNKNOWN`.
- [ ] Primary audiences named and labelled `EVIDENCED` or `HYPOTHESIS`.
- [ ] Top tasks ranked (3 to 5 drive the structure).

## B. Flows

- [ ] Every top task has a user flow with a happy path.
- [ ] Every top task has at least one failure path that ends in recovery.
- [ ] Realistic entry points listed (cold open, deep link, notification, return after interruption).
- [ ] Happy-path step count recorded; any task over budget has a written reason.

## C. Screens and states

- [ ] Every key screen has: user question, information priority, one primary action, destination, feedback, recovery.
- [ ] Required states specified (empty, loading, error, success at minimum where relevant).
- [ ] No screen has two competing primary actions without a reason.
- [ ] No dead ends: every error and empty state offers a next step.

## D. Navigation and labels

- [ ] Navigation model chosen with a reason tied to task frequency.
- [ ] Labels use user language; internal jargon flagged.
- [ ] Rare tasks may be hidden; frequent tasks are not.

## E. Wireframe spec

- [ ] Content blocks ordered by priority, each with a purpose line.
- [ ] Real content used; sample data marked `SAMPLE`.
- [ ] Behaviour on tap, empty, error and long text described.

## F. Walkthrough

- [ ] 5 scenario-based walkthroughs done, scenarios vary goal, confidence, device, failure and edge content.
- [ ] Each finding has screen, step, severity, fix, retest status.
- [ ] Zero open `blocker` findings.
- [ ] Evidence labelled `agent-heuristic` or `human`; no invented quotes or participant counts.

## Verdict

```text
UX Readiness: READY | READY_WITH_RISKS | NOT_READY
Open majors: <list or none>
Hypotheses to validate: <list or none>
Next validation step: <e.g. 5 moderated sessions on flows 1 and 3, or UNKNOWN>
```

`NOT_READY` blocks visual direction. `READY` does not mean the design is usable;
it means the structure is complete enough to design on and test.
