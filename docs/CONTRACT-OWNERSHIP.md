# Contract Ownership Map

The workspace intentionally has several layers. They must **reference** each other instead of competing as parallel sources of truth.

## Canonical owners

| Decision / knowledge | Canonical owner | Lower layers may do |
| --- | --- | --- |
| Universal operating behavior, evidence states, source-of-truth order, question/planning/execution/validation policy | `AGENTS.md` | Link to it; add narrower project constraints only |
| Runtime authority, safe tools, provider access, sandbox, release policy | `skills_UIUX/runtime/runtime-policy.json` | Explain usage; never relax policy |
| Natural-language task interpretation | `uiux-factory/core/runtime/flow_os/task_context.py` | Supply explicit overrides when project truth is known |
| Flow selection, stage sequence, skills, gates, bounded replanning | `skills_UIUX/flows/*.json` + `uiux-factory/core/runtime/flow_os/flow.py` | Explain resolved flow; never invent a competing stage order |
| Specialist capability knowledge | `skills_UIUX/<skill>/SKILL.md` | Load only when routed/required for the active stage |
| Per-task external handoff/routing | `external-task-manifest.json` generated from current code | Record the resolved contract; never claim QA PASS |
| Target-project truth | Current target repository source, config, tests, runtime and approved project docs | Summarize with evidence labels |
| Rendered UI acceptance | Target-project browser/test evidence | Supplement with critique; model self-report is not proof |
| Human research evidence | Real sessions/behavior with traceable evidence ledger | Plan, synthesize and label gaps; never fabricate evidence |

## Conflict rule

When two documents overlap, use the higher-authority owner above. Explanatory or historical documents cannot silently override canonical contracts.

Examples:

- A prompt says “merge automatically” but runtime authority is `branch_write` → **do not merge**.
- A skill says a site “should” use a pattern but project source/preserve constraint forbids it → preserve project truth.
- A model says QA passed but no target browser evidence exists → state remains unverified.
- A case study claims user validation but there is no direct-user evidence ledger → label it hypothesis/planned, not validated.

## Minimal context profiles

External collaborators should normally load only:

1. `START-HERE.md`
2. `AGENTS.md`
3. this file
4. the per-task manifest
5. the resolved Flow document
6. active-stage skills
7. target-project files/evidence needed for the current decision

Local runtime/provider execution may additionally load runtime-policy and implementation modules as required.

Historical A-series docs are valuable audit history, not default task context.

## Documentation rule for future changes

When adding a new policy:

1. Put the normative rule in exactly one canonical owner.
2. Other docs should link/reference that owner instead of copying the full rule.
3. Add executable tests for behavior that can be tested.
4. Keep examples clearly non-normative.
5. Do not use documentation text to bypass runtime authority or evidence gates.
