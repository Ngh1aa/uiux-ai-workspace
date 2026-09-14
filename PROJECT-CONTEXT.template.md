# Universal Project Context Template

Use this file as the reusable project-level input packet for AI work. Copy it to `PROJECT-CONTEXT.md` in a new project and fill only what is known. Keep unknown values explicit as `UNKNOWN` rather than guessing.

## Project identity

- **Project name:** [NAME]
- **Project type:** [Web / Mobile / Backend / AI / UIUX / Data / Research / Desktop / Other]
- **Repository / workspace:** [URL OR LOCATION]
- **Current stage:** [Research / Design / Implementation / QA / Production / Maintenance]

## Project goal

- **Primary goal:** [What the project must ultimately accomplish]
- **Success looks like:** [Concrete description of a successful project]
- **Primary users:** [Who uses it]
- **Main user problems:** [Problems being solved]

## UX / product problem frame

Fill what is known. Keep unsupported claims labeled with the evidence states at the end of this template.

- **Priority user / role:** [WHOSE TASK HAS PRIORITY]
- **Highest-value user task:** [JOB / TASK, NOT A FEATURE]
- **Observed friction / unmet need:** [WHAT IS HARD, UNCLEAR, RISKY OR INEFFICIENT]
- **Owner / business objective:** [WHAT THE ORGANIZATION NEEDS FROM THE SAME JOURNEY]
- **Primary behavior / conversion:** [DESIRED NEXT ACTION OR BEHAVIOR]
- **User value:** [WHAT BECOMES BETTER FOR THE USER]
- **Owner value:** [WHAT LEGITIMATE BUSINESS / PRODUCT VALUE IS SUPPORTED]
- **Critical journey:** [ENTRY → ORIENT → EVALUATE → ACT → CONFIRM / RECOVER]
- **Important alternate / recovery paths:** [...]
- **Evidence that could change the design:** [UNKNOWNS THAT MAY INVALIDATE THE CURRENT DIRECTION]

## Product success and measurement

A target is not a measured outcome. Do not invent baseline values or uplift.

- **Primary success signal:** [OBSERVABLE BEHAVIOR OR METRIC]
- **Secondary success signals:** [...]
- **Current baseline:** [VALUE + SOURCE / UNKNOWN]
- **Target:** [VALUE + RATIONALE / UNKNOWN]
- **Available analytics / logs / funnel data:** [...]
- **Business outcome evidence available:** [...]
- **Claims that must not be made:** [...]

## Research and validation access

- **Existing user research:** [FILES / FINDINGS / UNKNOWN]
- **Existing usability evidence:** [...]
- **Available participants / user roles:** [...]
- **Available stakeholder/domain experts:** [...]
- **Available developer / feasibility review:** [...]
- **Available accessibility review:** [...]
- **Available production analytics:** [...]
- **Validation methods that are feasible:** [USABILITY TEST / PROTOTYPE TEST / HEURISTIC / A11Y / ANALYTICS / A-B / OTHER]
- **High-risk hypotheses to test:** [...]

## Source of truth

- **Primary source of truth:** [Example: `src/`, `uiux-factory/`, `docs/spec.md`]
- **Architecture docs:** [FILES]
- **Requirements/spec:** [FILES]
- **Design source:** [FILES / FIGMA / DESIGN SYSTEM]
- **API/schema source:** [FILES]
- **Test source:** [FILES]
- **Deployment source:** [FILES / WORKFLOWS]

## Technology

- **Frontend:** [...]
- **Backend:** [...]
- **Database:** [...]
- **Languages:** [...]
- **Frameworks:** [...]
- **Important library versions:** [...]
- **Runtime:** [...]
- **Deployment:** [...]
- **External services:** [...]

## Architecture

- **Entry points:** [...]
- **Important modules:** [...]
- **Data flow:** [...]
- **Major dependencies:** [...]
- **Generated code:** [...]
- **Legacy/deprecated areas:** [...]
- **Areas that must not be modified:** [...]

## Constraints

### Must

- [...]

### Must not

- [...]

### Compatibility requirements

- [...]

### Performance requirements

- [...]

### Security requirements

- [...]

### Accessibility requirements

- [...]

### Browser/device requirements

- [...]

### Content / legal / operational requirements

- [...]

### Budget/time constraints

- [...]

## Design decision ledger

Use one row for each consequential product/UX decision. Do not invent alternatives after the fact simply to make the process look sophisticated.

| Decision | Evidence / hypothesis | User value | Owner value | Alternative(s) | Trade-off | Technical reality | Success signal | Risk / validation |
|---|---|---|---|---|---|---|---|---|
| [...] | [...] | [...] | [...] | [...] | [...] | [...] | [...] | [...] |

## Validation plan

For high-risk decisions, define validation before claiming an outcome.

| Hypothesis | Method | Participant / evidence source | Task / scenario | Success criteria | Current state | Finding / design response |
|---|---|---|---|---|---|---|
| [...] | [...] | [...] | [...] | [...] | PLANNED / OBSERVED / MEASURED / UNKNOWN | [...] |

Rules:

- Never fabricate participant counts, quotes, analytics, A/B results, conversion uplift or stakeholder feedback.
- If no real user validation exists, label the work `PLANNED VALIDATION`, `HEURISTIC REVIEW`, or another truthful method.
- Automated QA can prove implementation properties; it does not by itself prove user comprehension or business impact.

## Quality standard

- **Required tests:** [...]
- **Required build checks:** [...]
- **Required runtime verification:** [...]
- **Required visual verification:** [...]
- **Required performance checks:** [...]
- **Required accessibility checks:** [...]
- **Required usability / product validation:** [...]

## Project preferences

- **Coding style:** [...]
- **Naming convention:** [...]
- **Architecture preference:** [...]
- **Design preference:** [...]
- **Response language:** [Vietnamese / English / Other]
- **Preferred explanation depth:** [short / medium / detailed]

## Known issues

- [...]

## Current state

### What already works

- [...]

### What is incomplete

- [...]

### What recently changed

- [...]

### Known blockers

- [...]

## Reference material

- **Official documentation:** [...]
- **Reference products:** [...]
- **Competitors:** [...]
- **Research:** [...]
- **Do not copy:** [...]

## Portfolio / case-study capture

Capture this during the project rather than reconstructing a fictional process later.

- **Context / challenge:** [...]
- **My actual role and scope:** [...]
- **Important constraints:** [...]
- **Evidence available:** [...]
- **Important unknowns:** [...]
- **Core hypothesis:** [...]
- **Key decision and rationale:** [...]
- **Alternative / trade-off:** [...]
- **System / responsive / state behavior:** [...]
- **Implementation proof:** [...]
- **Validation performed:** [...]
- **Iteration caused by evidence:** [...]
- **Outcome that can be truthfully claimed:** [...]
- **What cannot be claimed:** [...]
- **Reflection / next validation:** [...]

## Definition of Done

The project or current milestone is considered complete when:

1. [...]
2. [...]
3. [...]
4. [...]

For UI/UX/product milestones, also confirm when relevant:

- the user problem and owner objective are both explicit;
- consequential decisions include rationale and trade-offs;
- critical journeys include meaningful recovery/state behavior;
- high-risk hypotheses map to validation methods;
- outcome claims are proportional to evidence;
- case-study capture preserves the real decision process.

## Evidence policy

Use these states consistently:

- `VERIFIED` — directly supported by evidence.
- `INFERRED` — reasonable conclusion from evidence.
- `ASSUMED` — temporary assumption required to proceed.
- `UNKNOWN` — insufficient evidence.

For validation artifacts you may additionally use:

- `PLANNED` — validation has been defined but not executed.
- `OBSERVED` — directly seen in a real review/test session, with source recorded.
- `MEASURED` — supported by recorded quantitative evidence.

Do not silently convert `UNKNOWN`, `ASSUMED` or `PLANNED` into facts or results.
