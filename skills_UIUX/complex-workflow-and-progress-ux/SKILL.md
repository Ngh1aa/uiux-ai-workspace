---
name: complex-workflow-and-progress-ux
description: Design long-running, multi-stage or interruptible workflows with ownership, progress, resumability and safe completion. Use for approvals, processing queues, applications, publishing flows or multi-actor enterprise tasks.
---

# Complex Workflow & Progress UX

## Workflow
1. Map stages, actors, dependencies and irreversible actions.
2. Separate user progress from backend processing status.
3. Show current state, blocker and next action.
4. Support draft/save/resume and cross-session continuation where useful.
5. Handle background jobs, queues, cancellation, retries and partial completion.
6. Design review, approval and audit history for multi-actor flows.

## Rules
- Do not fake percentage progress when duration is unknown.
- Use user-meaningful status language, not internal system states.
- Confirmation strength should match reversibility and consequence.

## Quality gate
Interrupted work can be recovered where business/user value warrants it, and no stage leaves ownership ambiguous.
