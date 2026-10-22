# Human-AI Pattern Reference

Read when you are writing the interaction table for a specific AI feature and need the guideline map, the required state inventory, or a model of a finished row. The main skill holds the decision rules; this file holds detail and an example.

## 1. Microsoft HAX guidelines mapped to design questions

| Phase | Guideline | Design question to answer in the spec |
|---|---|---|
| Initially | G1 Make clear what the system can do | Where does the scope line appear at point of use? |
| Initially | G2 Make clear how well the system can do it | What known weak spots do we state? |
| During | G3 Time services based on context | When does the AI interrupt, and when does it wait to be asked? |
| During | G4 Show contextually relevant information | What context from the current task does the AI use and show? |
| During | G5 Match relevant social norms | Does tone fit the domain and culture? |
| During | G6 Mitigate social biases | Which outputs were checked for stereotyping or exclusion? |
| When wrong | G7 Support efficient invocation | One step to call the AI? |
| When wrong | G8 Support efficient dismissal | One step to ignore or close, with no repeated nagging? |
| When wrong | G9 Support efficient correction | Can the user edit output inline? |
| When wrong | G10 Scope services when in doubt | Does it ask or narrow instead of guessing? |
| When wrong | G11 Make clear why the system did what it did | Is there a source or reason the user can verify? |
| Over time | G12 Remember recent interactions | What is remembered, for how long, and is it visible? |
| Over time | G13 Learn from user behavior | Which signals adapt the system, and is that disclosed? |
| Over time | G14 Update and adapt cautiously | Are changes gradual and non-disruptive? |
| Over time | G15 Encourage granular feedback | Can users say what was wrong, not only that it was? |
| Over time | G16 Convey the consequences of user actions | Does the user know how feedback or settings change behavior? |
| Over time | G17 Provide global controls | Off switch, memory clear, training opt-out where offered? |
| Over time | G18 Notify users about changes | How are model or policy changes announced? |

## 2. Required state inventory

| State | What the user sees | Required next step |
|---|---|---|
| Idle / invitation | Scope line plus 2 to 4 reliable examples | Start, or ignore without penalty |
| Thinking / streaming | Progress tied to real work; stop control | Stop keeps partial output |
| Success | Output with source or reason where claims are factual | Accept, edit, undo |
| Partial | What was done and what was skipped, and why | Continue, or finish manually |
| Low confidence | Highlighted uncertain parts, "Needs review" label | Review before use; manual path |
| Clarification | One focused question with suggested answers | Answer, or proceed with stated assumption |
| Refusal / out of scope | Plain reason category, no lecture | Rephrase hint, alternate tool or human contact |
| Error / timeout | What failed, whether input was kept | Retry with input preserved |
| Stopped by user | Partial work retained, no side effects beyond what was shown | Resume or discard |
| Changed behavior | Notice of model or policy change | Learn more, adjust settings |

## 3. Confidence display ladder

Choose the lowest rung that changes user behavior.

1. No display: errors are cheap and obvious.
2. Categorical flag: "Needs review" on outputs below an internal threshold.
3. Span-level highlighting: mark the uncertain field, sentence or cell.
4. Alternatives: show 2 or 3 options when the model is split.
5. Numeric score: only if calibrated on representative data and users were tested interpreting it.

## 4. Agentic action preview pattern

Before any action with an external effect:

- Plan list in plain verbs ("Send 3 emails to: ...", "Book a refundable fare under 400 USD").
- Each external effect marked, with the irreversible ones visually distinct and named.
- Approve all, approve per step, edit plan, cancel.
- During the run: current step, stop control, log of completed effects.
- After: summary of what changed, with undo where the platform allows and a clear statement where it does not.

## 5. Feedback control copy

State the consequence beside the control:

- "Rate this answer. Ratings are reviewed by our team and are not used to train models." (Use the true policy.)
- "Report a problem: tell us what was wrong" with categories: inaccurate, missing information, unsafe, other.

Do not imply learning that does not happen.

## 6. Worked example: AI summary in a support-ticket tool

**Before**

- Button "AI Magic" generates a summary that replaces the ticket description field.
- Badge "97% accurate" (a marketing figure, not per-output).
- Only control: regenerate. No undo; original description is overwritten.
- On failure: "Something went wrong."
- Thumbs up/down with "Helps improve our AI", no defined pipeline.
- Agent mode can auto-reply to the customer from the summary.

**After**

- Button "Summarize thread" with scope line: "Summarizes messages in this ticket. May miss attachments and images."
- Summary appears in a separate panel; description is untouched. Insert, edit and undo are one step each.
- Each bullet links to the message it came from; bullets with weak support are marked "Check source".
- Failure states: too long ("Summarized the latest 50 messages; older ones skipped"), refusal ("Cannot summarize messages flagged as sensitive. Open them directly."), timeout with retry keeping settings.
- Feedback: "Was this summary useful? Your rating is reviewed by the support tools team."
- Auto-reply removed from agent mode; drafting a reply is allowed, sending requires the agent to click Send on the specific draft.

**Filled interaction row**

| AI moment | User goal | Autonomy | Capability/limit copy | Confidence or source display | Control (accept/edit/undo/stop) | Failure state and next step | Data-use note | Guideline ref |
|---|---|---|---|---|---|---|---|---|
| Ticket summary | Grasp a long thread before replying | Suggest (medium cost, reversible) | "Summarizes messages in this ticket. May miss attachments." | Per-bullet source link; "Check source" flag on weak support | Insert, edit inline, undo, stop while streaming | Refusal names sensitive-message reason and offers opening messages directly | "Ratings reviewed by team, not used for training" | G1, G2, G9, G10, G11, G15 |

## 7. Review checklist for design critique

- Did we see the feature fail on real data?
- Would a new user predict what it cannot do?
- Is every claim checkable in under one click?
- Can a user complete the task with the AI turned off?
