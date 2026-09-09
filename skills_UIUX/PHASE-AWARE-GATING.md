# Phase-Aware Gating — Prevent False BLOCKED Lifecycle States

This document defines the canonical requirement-state model for multi-phase website projects using `skills_UIUX`.

## Problem this fixes

A project can become permanently `BLOCKED` when a prompt:

1. allows only `DONE_VERIFIED | BLOCKED | N/A_JUSTIFIED`;
2. requires future QA/regression/release requirements to be present from Phase 1;
3. maps every `PARTIAL` or `UNVERIFIED` result to `BLOCKED`;
4. requires `BLOCKED = 0` before advancing.

That state machine has no legal state for a requirement that is applicable but whose authoritative verification belongs to a later phase.

Example:

- Phase 1 defines production smoke as a release requirement.
- Production smoke cannot be verified before implementation/release.
- It is not `DONE_VERIFIED`.
- It is not `N/A_JUSTIFIED` because production may still be planned.
- Under a three-state ledger it becomes `BLOCKED`.
- Phase 1 then cannot pass even though the blocker is artificial.

## Canonical requirement states

Use four states:

```text
DONE_VERIFIED
N/A_JUSTIFIED
PENDING_FUTURE_PHASE
BLOCKED
```

Every material/applicable requirement should have:

```text
ID
Requirement
OWNER_PHASE
Status
Verification method
Evidence / rationale
```

## State definitions

### DONE_VERIFIED

The requirement is due in the current/owning phase, the required verification was performed, and the pass condition is satisfied.

### N/A_JUSTIFIED

The requirement is outside the declared scope/mode/authority and the rationale is explicit.

Examples:

- mobile/tablet when project scope is explicitly `desktop_only`;
- deployment when `release_authorization = no_release`;
- OLD→NEW comparison for a genuinely new website with no old baseline.

### PENDING_FUTURE_PHASE

The requirement is real and applicable, but its authoritative verification belongs to a later phase.

It MUST include:

- owner phase;
- expected verification method;
- any dependency needed before it can be verified.

This is not a fake pass. When its owner phase arrives, it must become `DONE_VERIFIED`, `N/A_JUSTIFIED`, or `BLOCKED`.

### BLOCKED

Use only when a requirement that is **due now** cannot be satisfied, a material decision cannot be made safely, authority is missing for an action the user requested, or a real defect/conflict prevents the phase from exiting.

## Phase-aware skill-result mapping

Replace this legacy rule:

```text
PASS -> DONE_VERIFIED
N/A -> N/A_JUSTIFIED
FAIL/PARTIAL/UNVERIFIED -> BLOCKED
```

with:

```text
PASS -> DONE_VERIFIED
N/A + rationale -> N/A_JUSTIFIED
FAIL -> BLOCKED when requirement is due now
PARTIAL / UNVERIFIED -> BLOCKED only when current phase requires that verification to exit
PARTIAL / UNVERIFIED for a later phase -> PENDING_FUTURE_PHASE
UNKNOWN fact -> keep UNKNOWN; block only when that unknown prevents a current-phase material decision/claim
```

## Phase exit rule

A phase may be `PASSED` when:

```text
all DUE-NOW requirements accounted = yes
current-phase BLOCKED = 0
current-phase UNACCOUNTED = 0
exit criteria verified = yes
all PENDING_FUTURE_PHASE items have owner + verification plan = yes
```

Do not require evidence that can only exist in a future phase.

Do not keep an item pending after its owner phase arrives merely to manufacture a pass.

## Durable phase handoff

Use:

```text
docs/uiux/Phase-State.md
```

Recommended fields:

```yaml
skill_ref: <immutable commit SHA>
phase: 1
result: PASSED
project_commit: <SHA or N/A>
due_now_blocked: 0
due_now_unaccounted: 0
pending_future_phase: 8
pending_by_owner:
  phase_2: 5
  phase_3: 2
  phase_4: 1
```

Downstream phases should read this artifact instead of relying on a literal `PHASE X RESULT = PASSED` sentence remaining in chat history.

## Skill-Version-Lock bootstrap

If `docs/uiux/Skill-Version-Lock.md` does not exist before Phase 1, Phase 1 may resolve the intended immutable skill ref and create the file.

The missing lock before its bootstrap step is not a blocker.

After it is created, later phases must use the same ref unless there is an explicit reviewed migration.

## Release authorization

If:

```text
release_authorization = no_release
```

then release/deployment is intentionally outside current authority.

Correct handling:

```text
Phase 4 / release scope = N/A_JUSTIFIED
```

Do not run a release phase and return `BLOCKED` merely because the configuration deliberately says not to release.

If the user explicitly asks for release and required authority is absent or ambiguous, then the release action is genuinely `BLOCKED`.

## Project mode

Do not default every design/redesign project to `production_candidate`.

Use `interactive_prototype` when the work is primarily design/implementation and production integrations/release evidence are not yet available.

Use `production_candidate` only when the project actually requires production-level integration, security/privacy, performance/browser, release and rollback verification.

## Desktop-only scope

If the declared project scope is:

```text
scope: desktop_only
```

then desktop viewports and declared pressure points are due-now requirements.

Mobile/tablet should be:

```text
N/A_JUSTIFIED
```

Do not claim `fully responsive`.

Generic mobile transformation guidance must not override an explicit user/project desktop-only scope.

## Visual evidence

Rendered visual QA remains a hard gate when the phase makes a visual-completion claim.

Correct distinction:

- Phase 1 research/design contract: future NEW rendered QA can be `PENDING_FUTURE_PHASE`.
- Phase 2 implementation representative-page gate: rendered evidence is due now; missing evidence can be `BLOCKED`.
- Final QA: required screenshots/routes are due now; missing inspection is `BLOCKED`.

Build success still does not replace rendered visual inspection.

## Migration checklist for existing Project Instructions

Replace or remove any rule equivalent to:

```text
Requirement chỉ có ba trạng thái.
FAIL/PARTIAL/UNVERIFIED -> BLOCKED.
Phase chỉ pass khi toàn lifecycle BLOCKED = 0.
```

Add:

```text
PENDING_FUTURE_PHASE
OWNER_PHASE
DUE_NOW exit accounting
Phase-State.md durable handoff
no_release -> release N/A_JUSTIFIED
```

## Core principle

> A rigorous gate should block missing evidence that is required **now**, not evidence that cannot legally exist until a later lifecycle phase.

This rule does not lower quality. It removes false blockers while keeping current-phase claims evidence-backed.