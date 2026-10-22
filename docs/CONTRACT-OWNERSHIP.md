# Contract Ownership Map

The workspace intentionally has several layers. They must **reference** each other instead of competing as parallel sources of truth.

## Canonical owners

| Decision / knowledge | Canonical owner | Lower layers may do |
| --- | --- | --- |
| Universal operating behavior, evidence states, source-of-truth order, question/planning/execution/validation policy | `AGENTS.md` | Link to it; add narrower project constraints only |
| Runtime authority, safe tools, provider access, sandbox, release policy | `skills_UIUX/runtime/runtime-policy.json` | Explain usage; never relax policy |
| Natural-language task interpretation | `uiux-factory/core/runtime/flow_os/task_context.py` | Interpret current user/task language; it does not own target-repository identity truth |
| Bounded target-project routing truth and routing-field provenance | `uiux-factory/core/runtime/flow_os/target_truth.py` | Read only declared target metadata sources; may influence routing fields only, never authority/gates/evidence/release |
| External Task Contract merge / routing precedence before Flow planning | `uiux-factory/core/runtime/flow_os/external_task.py` | Apply explicit caller overrides, target truth and task inference under the canonical precedence/coherence rules |
| External consumer model/capability preflight and compute-efficiency advice | `uiux-factory/core/runtime/flow_os/execution_advisor.py` + `skills_UIUX/runtime/runtime-policy.json` | Recommend a provider-neutral capability/reasoning floor, progressive context plan and checkpoint strategy; never switch the ChatGPT/Codex model, lower the quality floor, change authority, satisfy gates or authorize release |
| Flow selection, stage sequence, skills, gates, bounded replanning | `skills_UIUX/flows/*.json` + `uiux-factory/core/runtime/flow_os/flow.py` | Explain resolved flow; never invent a competing stage order |
| Multi-intent work decomposition and per-segment Flow ownership | `uiux-factory/core/runtime/flow_os/sequence_router.py` + `sequence_flow.py` | Preserve explicit segment order/scope; do not collapse multiple work owners into one flow |
| Stateful segment eligibility, dependency/artifact gates and rerun/reset semantics | `uiux-factory/core/runtime/flow_os/work_execution.py` | Ask which node is runnable and record validated handoff artifacts; never execute a blocked node |
| Concrete runner dispatch, artifact registry/checkpoint and bounded repair coordination | `uiux-factory/core/runtime/flow_os/execution_driver.py` | Execute only the runnable segment through a supplied runner; runner output still must satisfy the P1.5 gate |
| Git/GitHub target mutation transaction, branch lease/CAS, commit provenance, preview boundary and PR finalization | `uiux-factory/core/runtime/flow_os/github_transaction.py` | Mutate only the deterministic transaction branch, preserve P1.6 request/result semantics, create/reuse a PR after QA; never select flows, bypass evidence gates, push the base branch, or merge |
| External provider configuration attestation and canonical idle-integration truth | `uiux-factory/core/runtime/flow_os/provider_attestation.py` | Combine repository-static evidence, recent GitHub provider evidence and opt-in read-only provider API attestation; never equate missing activity with integration removal, persist credentials, mutate provider config, deploy, merge or release |
| Scheduled/continuous provider monitoring severity and credential-aware workflow disposition | `uiux-factory/core/runtime/flow_os/continuous_provider_truth.py` | Treat missing opt-in provider credentials as explicit degraded coverage, not a workflow failure; still fail on drift, conflicts, non-credential evidence gaps or configured-credential visibility failures; never weaken canonical provider truth or authorize mutation |
| Fleet-level scheduled provider truth completeness and aggregate health | `uiux-factory/core/runtime/flow_os/provider_truth_fleet.py` | Aggregate per-repository P1.7.10 artifacts, fail closed on missing/duplicate/unregistered fleet evidence, preserve degraded optional-credential states as nonblocking, and never create issues/PRs or mutate providers as an alert side effect |
| Historical provider-truth baseline selection and transition/delta detection | `uiux-factory/core/runtime/flow_os/provider_truth_history.py` + `provider_truth_transition.py` | Compare the current P1.7.11 fleet artifact with the newest previous successfully produced fleet artifact; emit transition evidence only, treat first-run baseline absence as nonblocking, and never create alerts/issues or mutate runtime/provider state |
| Specialist capability knowledge | `skills_UIUX/<skill>/SKILL.md` | Load only when routed/required for the active stage |
| Professional lifecycle deliverables and active-stage work cards | `skills_UIUX/website-delivery-pipeline/data/lifecycle.json` via `uiux-factory/core/skills/website_delivery.py` | External and managed packets share this owner; record checker verifies file coverage/freshness only and never substitutes Flow gates, human research, approval or visual judgment |
| Mobile design lifecycle work cards and curated platform knowledge | `skills_UIUX/mobile-app-design/data/lifecycle.json` + `data/sources.json` via the same `core/skills/website_delivery.py` owner | Platform-aware packets use existing Flow OS/authority; no copied UI kits, native implementation, runtime QA or store-release authority is implied |
| Mobile browser presentation and client-link handoff | `skills_UIUX/mobile-web-preview/SKILL.md` + `flows/mobile-web-preview.json`, with `browser_preview_stages` in the mobile lifecycle catalog | Reuse target components/state, browser QA and existing deployment-truth contracts; no new authority, native QA owner or automatic publication |
| Rendered focus smoke | `uiux-factory/qa/scripts/focus-audit.js` via browser QA; receipt validation in `core/runtime/flow_os/evidence.py` | Static frontend focus flags remain source lint; ambiguous rendered indicators require review, not a fabricated PASS or WCAG conformance claim |
| Page-job design candidates, quantitative hypotheses and structured domain cues | `skills_UIUX/visual-design-direction/data/design-knowledge.json` via `uiux-factory/core/skills/design_knowledge.py` | Retrieve one role after identity is known; never turn candidate ranges into brand facts or universal presets |
| Design decision/capture integrity | `uiux-factory/core/skills/design_decisions.py` + `skills_UIUX/visual-design-direction/scripts/check-design-decisions.py` | Emit canonical typed integrity receipts; never certify beauty, independently inspected pixels or human preference |
| UX structure integrity (flows, screens, walkthrough, UX Readiness) | `uiux-factory/core/skills/ux_structure.py` + `skills_UIUX/ux-structure-and-flow-design/scripts/check-ux-structure.py` | Check structural completeness and honest evidence labels before visual direction; export `pages[].ux` for the design contract; never certify usability or participant behaviour |
| UX prerequisites for visual acceptance | `pages[].ux` in the same design decision schema; `ux_contract_required` in existing Flow gates | Record task/action/feedback/recovery and walkthrough findings; reject unresolved blockers and missing retest, but never treat record coverage as human usability proof |
| Domain/page-role reference anatomy | `skills_UIUX/visual-design-direction/data/reference-anatomies.json` via the shared `design_knowledge.py` retrieval | Return only matched role cards and source observations; transfer geometry/type/density remain hypotheses until rendered inspection |
| Domain workflow candidates | `skills_UIUX/visual-design-direction/data/domain-workflows.json` via the same `design_knowledge.py` lookup | Retrieve actors/state/recovery/metrics for one supported identity + role; no eager deep load, clinical policy, outcome proof or authority effect |
| Skill-change paired descriptive comparison | `skills_UIUX/scripts/eval-harness.py` + `evals/CONTROLLED-COMPARISON.md` | Validate declared matched pairs and retain regressions; no new execution orchestrator, causal uplift, human preference or beauty claim |
| Deliberate decision practice | `skills_UIUX/visual-design-direction/references/decision-practice.md` | Rehearse existing owner skills with authored examples, critique and retest; never override the task Flow or certify mastery |
| Counterbalanced direction comparison and recorded comprehension/distinctiveness | `uiux-factory/core/skills/design_comparison.py` + `skills_UIUX/visual-design-direction/scripts/evaluate-design-comparison.py` | Prepare label/question packets and summarize capture-bound observations; never generate human sessions, causal conclusions, a beauty PASS or an automatic winner |
| Per-task external handoff/routing | `external-task-manifest.json` generated from current code | Record the resolved contract and provenance; never claim QA PASS |
| GitHub-native external-collaborator control plane | `.github/workflows/external-agent-runner.yml` + `skills_UIUX/scripts/github-external-agent-runner.py` | Checkout target truth, compile/transport the governed task packet and declared verification; never pretend to execute an LLM provider |
| GitHub-connector bounded ingress when direct workflow dispatch is unavailable | `.github/workflows/external-agent-connector-bridge.yml` + `skills_UIUX/scripts/github-connector-task-request.py` | Accept trusted issue metadata, validate a fixed request schema, then reuse the canonical external-agent runner; never accept install/build/serve shell commands from issue text |
| Target-project truth | Current target repository source, config, tests, runtime and approved project docs | Supply routing metadata and execution evidence through bounded adapters; source truth never grants Factory authority by itself |
| Rendered UI acceptance | Target-project browser/test evidence | Supplement with critique; model self-report is not proof |
| Visual-signature compatibility during non-redesign migrations | `docs/VISUAL-SIGNATURE-REGRESSION-CONTRACT.md` + target-project declared invariants | Declare project-specific media/motion/composition/page-role invariants; never force a signature pattern that the project does not have |
| Lifecycle-state semantic acceptance | Target project's State Coverage contract + `uiux-factory/qa/scripts/state-coverage.mjs` | Declare state query/assertions/focus; cannot waive required semantic evidence after a rendered failure |
| Infrastructure/release failure taxonomy | `uiux-factory/qa/scripts/infra-failure-classifier.mjs` | Add provider evidence text; do not relabel product QA failures as infra noise |
| Deployment truth acceptance | `uiux-factory/qa/scripts/deployment-truth.mjs` + `.github/workflows/deployment-truth-gate.yml` | Supply provider/API deployment metadata and production URL; never manufacture provider SHA from the expected source SHA |
| Release-level evidence registry | `uiux-factory/core/provenance/release_evidence_registry.py` + `core/contracts/release_evidence_schema.py` | Register/hash artifacts and derived claim state; never override the originating gate's evidence semantics |
| Fine-grained evidence lineage | `uiux-factory/core/provenance/evidence_lineage.py` + evidence provenance contracts | Produce individually addressable evidence/spec links beneath the release registry |
| Human research evidence | Real sessions/behavior with traceable evidence ledger | Plan, synthesize and label gaps; never fabricate evidence |

## External routing precedence

When compiling an external collaborator manifest from a checked-out target, current routing uses:

```text
explicit caller override
> structured target-project routing truth
> natural-language goal inference
```

This is not permission for project files to override current user intent indiscriminately. Stable project identity can correct routing inference; project lifecycle metadata acts as a bounded default; fallback README/package inference only fills generic identity gaps; explicit caller overrides remain highest priority. The canonical merge/coherence behavior lives in `core/runtime/flow_os/external_task.py` and its provenance is emitted in the manifest.

Authority is outside this target-truth precedence. Effective authority still comes from runtime policy plus caller/task authorization. A target file cannot grant merge, deploy, release, provider, evidence or gate authority.

## GitHub production transaction boundary

P1.7 deliberately sits *below* routing and execution-state ownership:

```text
Task/target truth
→ Flow + sequence routing
→ WorkExecutionPlan (P1.5)
→ ExecutionDriver (P1.6)
→ GitHubProductionRunner transaction (P1.7)
```

The GitHub transaction runner may clone/fetch the target, claim one deterministic transaction branch, invoke the already-routed segment worker, commit implementation changes, run a declared preview command, collect QA evidence, and create or reuse a pull request. It may not choose a different stage, add its own specialist routing, mark missing evidence as PASS, push the configured base branch, or merge the PR.

Transaction isolation uses two fences: an atomic local TTL lease for same-workspace concurrency and remote branch provenance plus compare-and-swap push (`--force-with-lease`) for distributed mutation safety. A branch that moves outside the expected transaction/lease provenance fails closed rather than being overwritten.

A transaction PR is a handoff artifact, not release proof. Deployment and release truth remain owned by the deployment/evidence contracts above.

### Executor contract 2.0 migration

`execution_driver.py` owns the 2.0 request/result/checkpoint boundary. Executing callers
must supply `ExecutionGrant`; routing and target truth cannot grant permissions. A
read-only goal can reduce that grant. Requests carry the effective authority, absolute
artifact workspace, plan fingerprint and explicit approval status. Both the driver
and concrete adapters validate these controls before invoking a runner. Legacy 1.0
requests/results/checkpoints fail closed; resume requires the same caller grant.
Concrete adapters bind the caller's plan fingerprint before dispatch. Checkpoints
retain typed evidence per passed stage; resume rechecks canonical nodes, accepted
outputs, current hashes and evidence gates, including a fully completed checkpoint.
It does not accept a stored PASS as proof and does not overwrite a rejected checkpoint.

Host `CommandRunnerAdapter` commands are trusted caller-supplied programs and require
at least `branch_write`, including audit runs which can write artifacts. They are not
a sandbox for model-generated or untrusted target commands; those use the existing
`ToolRegistry`/`ContainerSandbox` boundary. GitHub transaction brokers require
`external_write` before checkout/branch claims/worker invocation. SegmentRunner
implementations must declare their required authority; undeclared adapters fail closed.

The existing `auto` policy remains explicit `UNREVIEWED`, never human approval.
In `manual` mode, stage execution approval is bound to the current plan fingerprint
and obtained through `approve_stage`; this permission to execute is not a claim of
human usability validation. Read-only research requires no execution approval.
Pure planning, packet compilation and handoff helpers do not execute a runner and do
not grant completion, write, merge or release authority.

All passing executor results must carry typed runtime `evidence_records`, bound to
current local proof artifacts; screenshot labels and prose are insufficient. The
shared `validate_runner_evidence` boundary runs in the driver, command adapter, and
GitHub broker before implementation commit/push or PR finalization. File handoff
digests are checked again before dispatch. Release rechecks current rendered bytes.
These are consistency/provenance checks for trusted runtime adapters, not a signature
scheme that authenticates a hostile caller or proves usability/design quality.
Before publishing, command adapters and GitHub brokers also reuse `ArtifactRegistry`
path/hash validation and the expected-output owner in `work_execution.py`. QA outputs
cannot be absent, mislabeled, stale, outside the workspace, or reuse an input ID before
PR creation. The broker owns the implementation commit output; workers supply all
other required kinds, and the final Driver still requires the real broker commit.
Required `qa-evidence` outputs must declare both a workspace file path and its
current `sha256:` digest. URI-only outputs and metadata-only path claims are
rejected before PR creation and again on checkpoint resume. Producers must hash
the final selected file after any render/path substitution. This requirement does
not apply to broker-owned implementation commit and pull-request URIs.

Native internal implementation and repair callers must pass `execution_grant` into
`run`, `run_revision`, or `RunContext`. `run.py --authority branch_write` is the explicit
write opt-in; omission defaults to `read_only`. The shared frozen-spec verifier in
`run_context.py` is used by managers, direct AI builders and QA/repair loops. Manual
native execution approval binds to the current spec SHA; auto remains unreviewed.
Prompt packs and native spec manifests use schema 2. The deterministic compiler
owns the specification from `RunContext.goal` and the eight upstream artifacts
listed in `prompt_pack_schema.py::SPEC_UPSTREAM_ARTIFACTS`. Both compiler wrappers
bind these inputs and their generated content; `specification_compile` is excluded
from provider refinement in both team runners. Change the goal/upstream and
recompile to change the specification. A provider must not reseal its own edits.
The shared verifier rechecks current upstream, spec and implementation-prompt
hashes before implementation/repair. Legacy manifests without binding must be
recompiled; they are not auto-upgraded on resume.
The retained `*_consistent` flag names are compatibility names for structural
checks (routes/page roles/domain/responsive/QA references), not semantic validation.
`upstream_binding_valid` additionally detects missing, changed or stale inputs and
compiled content. Hashes establish consistency for trusted owners, not authenticity
against a hostile local writer, correctness of prose, human approval or design quality.
Native BrowserQA emits screenshot SHA and validates the declared route/viewport
matrix before visual critique. P1.7.1 source-only QA now fails closed: operators must
produce current browser evidence inside the transaction workspace and supply
`--browser-artifact-dir` (or the worker's default `evidence/browser` directory).
No consumer may synthesize render evidence to keep a production run passing.

## Conflict rule

When two documents overlap, use the higher-authority owner above. Explanatory or historical documents cannot silently override canonical contracts.

Examples:

- A prompt says “merge automatically” but runtime authority is `branch_write` → **do not merge**.
- A target `.uiux-profile.json` says `release_authorization=merge_and_deploy` but the current task/caller has only `branch_write` → target truth may affect routing identity, **not** authority.
- A terse prompt says “continue this project” while a checked-out structured project profile says `website_type=portfolio` → the bounded target-truth adapter may supply the portfolio identity before Flow planning, with provenance.
- A README fallback says fintech while the current task specifically identifies an art museum → specific task identity wins over fallback inference.
- A skill says a site “should” use a pattern but project source/preserve constraint forbids it → preserve project truth.
- A model says QA passed but no target browser evidence exists → state remains unverified.
- A P1.7 worker tries to edit target files during audit/design/QA → revert that read-only mutation and fail the segment; only the implementation/repair owner may create target commits.
- A P1.7 transaction branch moved since the last observed remote SHA → fail the lease/ownership fence instead of force-overwriting the other writer.
- A P1.7 PR already exists for the same deterministic head/base pair → reuse it; do not create a duplicate PR.
- A content/evidence migration makes copy and accessibility checks greener but silently removes an existing hero media/motion/composition invariant → rendered acceptance fails; repair the visual owner or record an explicitly authorized redesign.
- A state URL says `state=empty` but the contract's Empty semantic marker is absent → State Coverage fails even if HTTP/console checks are green.
- A provider reports `build-rate-limit / upgradeToPro` while rendered product QA is green → classify provider capacity separately; do not rewrite product code to manufacture a deployment PASS.
- Deployment metadata points at a different SHA than the intended release → release is not `DEPLOYED_VERIFIED`, even if the production URL returns 200.
- A release registry is missing a state/deployment artifact → the corresponding claim stays `UNKNOWN`; an artifact inventory is not permission to invent a PASS.
- A case study claims user validation but there is no direct-user evidence ledger → label it hypothesis/planned, not validated.
- A connector task issue includes `install_command`, `build_command` or `serve_command` → reject the request at the bridge; connector ingress is metadata-only and cannot create an arbitrary shell execution path.

## Minimal context profiles

External collaborators should normally load only:

1. `START-HERE.md`
2. `AGENTS.md`
3. this file
4. the per-task manifest
5. the resolved Flow document
6. active-stage skills
7. target-project files/evidence needed for the current decision

The manifest itself records bounded target-truth provenance; collaborators should not reload the entire target repository merely to repeat routing inference. They still audit the actual files relevant to implementation before mutation.

For a task that can change an existing rendered UI, Home/top-of-page composition, design-system rendering, media, motion, or a mass content/evidence migration, also load `docs/VISUAL-SIGNATURE-REGRESSION-CONTRACT.md` and the target project's declared visual-signature invariants when they exist. The external-task manifest automatically includes this contract in `canonical_sources` when the interpreted task indicates an existing-UI compatibility boundary; explicit full redesigns do not pay that context cost unless preserve/forbidden constraints reactivate it.

Local runtime/provider execution may additionally load runtime-policy and implementation modules as required.

Historical A-series docs are valuable audit history, not default task context.

## Documentation rule for future changes

When adding a new policy:

1. Put the normative rule in exactly one canonical owner.
2. Other docs should link/reference that owner instead of copying the full rule.
3. Add executable tests for behavior that can be tested.
4. Keep examples clearly non-normative.
5. Do not use documentation text to bypass runtime authority or evidence gates.
