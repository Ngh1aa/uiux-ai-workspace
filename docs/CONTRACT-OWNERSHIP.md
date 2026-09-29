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
| GitHub-native external-collaborator control plane | `.github/workflows/external-agent-runner.yml` + `skills_UIUX/scripts/github-external-agent-runner.py` | Compile/transport the governed task packet and declared verification; never pretend to execute an LLM provider |
| Target-project truth | Current target repository source, config, tests, runtime and approved project docs | Summarize with evidence labels |
| Rendered UI acceptance | Target-project browser/test evidence | Supplement with critique; model self-report is not proof |
| Visual-signature compatibility during non-redesign migrations | `docs/VISUAL-SIGNATURE-REGRESSION-CONTRACT.md` + target-project declared invariants | Declare project-specific media/motion/composition/page-role invariants; never force a signature pattern that the project does not have |
| Lifecycle-state semantic acceptance | Target project's State Coverage contract + `uiux-factory/qa/scripts/state-coverage.mjs` | Declare state query/assertions/focus; cannot waive required semantic evidence after a rendered failure |
| Infrastructure/release failure taxonomy | `uiux-factory/qa/scripts/infra-failure-classifier.mjs` | Add provider evidence text; do not relabel product QA failures as infra noise |
| Deployment truth acceptance | `uiux-factory/qa/scripts/deployment-truth.mjs` + `.github/workflows/deployment-truth-gate.yml` | Supply provider/API deployment metadata and production URL; never manufacture provider SHA from the expected source SHA |
| Release-level evidence registry | `uiux-factory/core/provenance/release_evidence_registry.py` + `core/contracts/release_evidence_schema.py` | Register/hash artifacts and derived claim state; never override the originating gate's evidence semantics |
| Fine-grained evidence lineage | `uiux-factory/core/provenance/evidence_lineage.py` + evidence provenance contracts | Produce individually addressable evidence/spec links beneath the release registry |
| Human research evidence | Real sessions/behavior with traceable evidence ledger | Plan, synthesize and label gaps; never fabricate evidence |

## Conflict rule

When two documents overlap, use the higher-authority owner above. Explanatory or historical documents cannot silently override canonical contracts.

Examples:

- A prompt says “merge automatically” but runtime authority is `branch_write` → **do not merge**.
- A skill says a site “should” use a pattern but project source/preserve constraint forbids it → preserve project truth.
- A model says QA passed but no target browser evidence exists → state remains unverified.
- A content/evidence migration makes copy and accessibility checks greener but silently removes an existing hero media/motion/composition invariant → rendered acceptance fails; repair the visual owner or record an explicitly authorized redesign.
- A state URL says `state=empty` but the contract's Empty semantic marker is absent → State Coverage fails even if HTTP/console checks are green.
- A provider reports `build-rate-limit / upgradeToPro` while rendered product QA is green → classify provider capacity separately; do not rewrite product code to manufacture a deployment PASS.
- Deployment metadata points at a different SHA than the intended release → release is not `DEPLOYED_VERIFIED`, even if the production URL returns 200.
- A release registry is missing a state/deployment artifact → the corresponding claim stays `UNKNOWN`; an artifact inventory is not permission to invent a PASS.
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

For a task that can change an existing rendered UI, Home/top-of-page composition, design-system rendering, media, motion, or a mass content/evidence migration, also load `docs/VISUAL-SIGNATURE-REGRESSION-CONTRACT.md` and the target project's declared visual-signature invariants when they exist.

Local runtime/provider execution may additionally load runtime-policy and implementation modules as required.

Historical A-series docs are valuable audit history, not default task context.

## Documentation rule for future changes

When adding a new policy:

1. Put the normative rule in exactly one canonical owner.
2. Other docs should link/reference that owner instead of copying the full rule.
3. Add executable tests for behavior that can be tested.
4. Keep examples clearly non-normative.
5. Do not use documentation text to bypass runtime authority or evidence gates.
