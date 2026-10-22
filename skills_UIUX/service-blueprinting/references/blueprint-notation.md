# Blueprint Notation Reference

Read this when you are drawing the canvas, choosing notation, interviewing backstage staff, or need a model of a filled blueprint row.

## 1. Lane definitions

| Lane | Contains | Typical sources | Common mistake |
|---|---|---|---|
| Evidence | Screens, emails, SMS, letters, receipts, signage, the user sees or keeps | Screenshots, templates, mailbox audit | Left blank after waits |
| Customer actions | What the user does, verb first | Research, analytics, support logs | Written as system steps |
| Frontstage | Staff or system actions the user directly experiences | Observation, scripts, UI | Mixing in invisible work |
| Backstage | Staff work out of user sight | Staff interviews, shadowing | Using the official SOP only |
| Support processes | Systems, internal teams, vendors, queues, data stores | Architecture docs, IT, vendors | Listing tools with no owner |

Lines:
- Line of interaction: separates customer actions from frontstage. Every crossing is a touchpoint.
- Line of visibility: separates what the user can see from what they cannot. Every crossing downward is a point where status communication is needed.
- Line of internal interaction: separates backstage staff from support systems and teams. Crossings are internal handoffs and integration points.

## 2. Markers

Use a consistent, legend-backed set. Text labels are required alongside any icon or color so the blueprint reads in grayscale and for screen-reader users.

| Marker | Meaning | Required fields |
|---|---|---|
| F | Fail point | Failure mode, detection (who, how), recovery, frequency if known |
| W | Wait point | Observed duration range, what user is told, source of the number |
| H | Handoff | Sender role, receiver role, medium (queue, email, ticket), data passed |
| G | Ownership gap | Handoff or step with no named owner |
| E? | Evidence gap | User action with no artifact confirming outcome |
| A | Assumed | Cell not yet verified; becomes a research question |

## 3. Interviewing backstage staff

- Ask for the last real case, not the usual process: "Walk me through the last application you handled."
- Ask where they keep side records (spreadsheets, notes, chat). These are hidden support systems.
- Ask what they do when information is missing. This is where fail points live.
- Ask how they learn the user is stuck. If the answer is "the user calls", detection is reactive.
- Ask who they pass work to and how they know it was received.

## 4. Classifying pain points

| Type | Test | Typical fix | UI role |
|---|---|---|---|
| UI | Service would succeed if the user understood or found the control | Redesign, copy, IA | Primary fix |
| Service | Process is slow, fails or needs unavailable input | Process change, staffing, integration | Interim: expectations, status, alternatives |
| Policy | A rule or law creates the friction | Policy review or accept | Explain the rule plainly |

Never ship a status display that implies progress the backstage cannot report. If the system cannot emit a status, the honest interim is an expectation ("Reviews take 2 to 5 working days; we email you when done") backed by real data.

## 5. Prioritization

Score opportunities on two axes, each low, medium or high, with evidence:
- User impact: frequency times severity (abandonment, contacts, harm, missed deadlines).
- Operational impact: cost, rework, staff time, risk.
Ownership gaps on critical handoffs go first regardless of score, because nothing else can be fixed reliably while nobody owns the step.

## 6. Worked example: filled rows (as-is, rental deposit refund)

Scenario: tenant moves out and wants their deposit back. End state: money received.

| Step | Evidence | Customer action | Frontstage (owner) | Backstage (owner) | Support systems (owner) | Wait (observed) | Fail point and detection | Problem type | Evidence quality |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Online form confirmation screen | Submits move-out form with bank details | Form validates IBAN (web team) | None | CRM record created (CRM admin) | None | F: bank details typed into free-text field, not validated; detected only at payout | UI | Observed |
| 2 | None (E?) | Waits for inspection | None | Property manager schedules inspection (property ops) | Shared spreadsheet calendar (G: no owner) | 3 to 12 days | F: request missed when spreadsheet not checked; detected when tenant calls | Service | Staff reported |
| 3 | Email with inspection result | Reads deductions | Email sent (property ops) | Manager enters deductions | Finance queue (finance team) | A: unknown | H: property ops to finance, via email to shared inbox, receiver unnamed (G) | Service | Assumed |

Before (UI-only reading): "Users call because the form is confusing. Redesign the form."

After (blueprint reading):
- Step 1 is a genuine UI fix: validated bank field.
- Step 2 is a service gap: no owner for the scheduling spreadsheet and no evidence to the tenant. Interim UI: send a confirmation stating the observed range and how to reschedule. Operational fix: named scheduler role and a real queue.
- Step 3 has an ownership gap at the finance handoff and an assumed wait. Research: pull finance timestamps for the last 50 refunds.

## 7. As-is versus to-be

- Build as-is first from evidence. Then copy it into a separate to-be canvas.
- In to-be, every changed cell links to the opportunity it implements.
- Keep the as-is version dated; it is the baseline for later service-health measurement.

## 8. Format

- A table is acceptable and often better for accessibility and diffs; a visual canvas is for workshops.
- Steps read left to right in time order. Parallel tracks get sub-rows, not overlapping sticky notes.
