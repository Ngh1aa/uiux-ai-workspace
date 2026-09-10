# Universal Task + Output Contract

Use this prompt for a concrete task after the project-level context is available.

## Task

- **Task:** [Exactly what you want done]
- **Why:** [Why this matters]
- **Desired outcome:** [Concrete end result]

## Scope

### In scope

- [...]

### Out of scope

- [...]

## Inputs

- **Relevant files:** [...]
- **Relevant URLs:** [...]
- **Relevant data:** [...]
- **Relevant previous work:** [...]
- **Screenshots/assets:** [...]

## Acceptance criteria

The task passes only if:

- [ ] [...]
- [ ] [...]
- [ ] [...]
- [ ] [...]

## Constraints

### Do

- [...]

### Do not

- [...]

### Preserve

- [...]

### Can change

- [...]

## Execution contract

Work autonomously.

Do not ask questions unless missing information is truly blocking and guessing would materially risk correctness.

Before modifying an existing system:

1. inspect the relevant source;
2. identify the source of truth;
3. understand dependencies and tests;
4. prefer root-cause fixes over symptom patches;
5. avoid unrelated changes.

Use available tools when they provide direct evidence.

For current or version-sensitive information, verify using up-to-date authoritative sources.

When execution is possible, continue through implementation and verification instead of stopping at recommendations.

## Verification contract

Determine, at minimum:

1. Does the implementation satisfy the requested behavior?
2. Do existing relevant tests still pass?
3. Are new tests or evidence needed?
4. Did the change introduce regressions in the affected surface?
5. Is there direct evidence supporting the completion claim?

### UI/frontend

When applicable, inspect actual rendered output, representative routes, responsive sizes, interaction states, console/runtime errors, and visual regressions.

### Backend/API

When applicable, test representative successful requests, invalid input, failure behavior, schemas/contracts, persistence, and authorization boundaries.

### Research

Use primary/official sources where possible and distinguish sourced facts from inference.

## Failure policy

If verification fails:

1. capture the failure evidence;
2. identify the earliest responsible owner/root cause;
3. repair or regenerate from that point;
4. rerun downstream validation;
5. do not repeatedly patch the same symptom without new evidence.

## Output contract

Return the final result using this structure for substantial tasks:

### Status

`DONE` / `PARTIAL` / `BLOCKED`

### Result

1–5 sentences describing the actual outcome.

### What changed

Only material changes.

### Verification

Tests, builds, runtime checks, screenshots, sources, or other direct evidence.

### Files / artifacts

Only important files changed or created.

### Remaining issues

Only real unresolved issues or unknowns.

### Recommended next step

Include only when genuinely useful.

Do not claim anything that was not verified.
