# Current Runtime Map

Status: **A55.1 CLOSED / POST-CLOSURE HARDENING CURRENT THROUGH P4 / WORKSPACE UPGRADE CLOSED WITH INTENTIONAL HOLDS**  
Audit date: **2026-10-03**  
Baseline before Flow 5 / A55.1: `main@7e75fc27780e4ded5fed59f51fdad893ad4f6ddf`  
Post-closure hardening baseline before P3: `main@4f8cf53b03164140561cd0c08ef3ce42158bad27`  
P4 coherence baseline: `main@7f2714e886aa8217f19bc80dc1839b2e2bdefe40`

This map describes current executable ownership, explicit holds, the completed bounded upgrade-closure boundary, and post-closure productization/reliability hardening. Historical A-series plans remain audit history; current source/tests and exact-head CI evidence are authoritative.

## 1. Product entry and shared Flow OS

Primary Factory lifecycle:

```text
uiux-factory/run.py
uiux-factory/core/manager/
```

Managed/provider-neutral entry:

```text
skills_UIUX/scripts/uiux-agent.py
```

Shared executable runtime owner:

```text
uiux-factory/core/runtime/flow_os/
```

The managed/provider-neutral entry shares canonical Flow OS and is **not a second Flow OS**.

Declarative ownership remains under:

```text
skills_UIUX/
skills_UIUX/flows/
skills_UIUX/runtime/runtime-policy.json
skills_UIUX/schemas/
skills_UIUX/<skill>/SKILL.md
```

## 2. Runtime compatibility surface

`skills_UIUX/runtime/*.py` remains compatibility-only.

Historical A52.3 census:

```text
shim_count = 8
internal_consumer_files = 8
internal_consumer_imports = 19
```

Flow 1 / A53.1 current census:

```text
shim_count = 8
internal_consumer_files = 0
internal_consumer_imports = 0
shim_contract_clear = true
identity_checks_clear = true
FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS
```

Flow 2 / A53.2 governance:

```text
retain_indefinitely = 0
deprecate_with_sunset = 8
open_removal_governance = 0
external_usage_status = UNKNOWN
earliest_removal_review_date = 2026-12-31
removal_governance_open = false
shim_deletion_allowed = false
```

Zero internal consumers does not prove external removal safety.

## 3. Provider layer

Current anchors:

```text
core/runtime/free_provider.py
core/runtime/provider_compat_contract.py
core/runtime/flow_os/provider*.py
core/runtime/flow_os/factory_provider_adapter.py
```

A48 historically reconciled **different provider entry/capability contracts**.

Current lane truth:

```text
legacy = default
managed_compat = explicit opt-in
no automatic cross-lane fallback
```

A51.1 current live-evidence state:

```text
collection_status = NOT_RUN
receipts = 0 / 8
decision = KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED
migration_governance_allowed = false
default_change_allowed = false
provider_migration_allowed = false
auto_migration_allowed = false
product_evidence = false
```

Flow 5 preserves this as an intentional hold.

## 4. Lifecycle layer

A49 reconciles **distinct top-level lifecycle APIs** through read-only projection.

Current mutation owners:

```text
Factory -> core.runtime.run_context.RunContext
Managed -> core.runtime.flow_os.managed.ManagedWebsiteRun
```

A52.1 current decision:

```text
KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED
```

Six semantic blockers remain:

```text
distinct_state_models
factory_append_only_chronology
managed_checkpoint_and_stage_lineage
managed_human_gate_semantics
replan_invalidation_semantics_non_parity
finalize_release_semantics_non_parity
```

A52.2 observation interoperability:

```text
core/runtime/lifecycle_event_interop.py
benchmarks/lifecycle-event-interop-v1.json
core/benchmarks/lifecycle_event_interop_regression.py
scripts/validate_lifecycle_event_interop.py
```

Chronology remains intentionally asymmetric:

```text
Factory -> durable_append_only
Managed -> derived_checkpoint_delta
```

Every interoperability receipt remains observation-only with execution/authority/gate/evidence/release effects `none`.

## 5. Evidence and provenance

Canonical current-run evidence owners:

```text
core/runtime/flow_os/evidence.py
core/provenance/
uiux-factory/qa/
```

Trusted evidence remains runtime-origin. Provider/model-authored claims remain untrusted and cannot become trusted PASS evidence by metadata alone.

## 6. Terminal evaluation

Canonical evaluator:

```text
core/evaluation/run_evaluator.py
```

Invariant:

```text
managed lifecycle COMPLETED
+ insufficient trusted PASS evidence
= insufficient_evidence
```

Completion is not release.

## 7. Brain OS

Bounded reasoning/control owner:

```text
uiux-factory/core/brain_os/
```

Implemented anchors:

```text
core/brain_os/contracts.py
core/brain_os/reasoning/evidence_graph.py
core/brain_os/critics/
core/brain_os/repair_orchestrator.py
core/brain_os/memory_contracts.py
core/memory/brain_memory.py
core/brain_os/adapters/memory_context.py
core/brain_os/scorecard.py
```

Brain OS is not a third runtime. Critique, repair proposals, memory, scorecards and retrieved knowledge remain advisory/proposal channels. They cannot override canonical runtime evaluation or release authority.

## 8. Knowledge OS

Canonical owners:

```text
skills_UIUX/knowledge/
skills_UIUX/knowledge/index.json
skills_UIUX/schemas/knowledge-record.schema.json
skills_UIUX/schemas/knowledge-index.schema.json
core/brain_os/knowledge_retrieval.py
core/brain_os/adapters/knowledge_context.py
```

Current canonical corpus is exactly five records:

```text
financial-services
art-culture
industrial-services
mobility-ev
education-edtech
```

Retrieval remains:

```text
deterministic_metadata_first = true
vector_search_used = false
advisory_only = true
current_run_evidence = false
```

GenAI/NIST remains `KEEP_HOLD_FRESHNESS_REVIEW`. Vector/semantic retrieval remains optional and requires separate product need + benchmark evidence.

## 9. Flow 3 architecture-debt state

Executable owner set:

```text
benchmarks/architecture-debt-closure-audit-v1.json
core/benchmarks/architecture_debt_closure_audit.py
scripts/validate_architecture_debt_closure_audit.py
tests/test_architecture_debt_closure_audit_a53.py
```

Current ledger:

```text
CLOSED = 4
INTENTIONAL_HOLD = 5
NEW_ACTIONABLE_DEBT = 0
ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE
```

The five intentional holds remain provider migration, lifecycle mutation convergence, GenAI/NIST expansion, vector/semantic retrieval, and compatibility-shim removal.

## 10. Flow 4 final regression

Executable owner set:

```text
benchmarks/final-upgrade-regression-v1.json
core/benchmarks/final_upgrade_regression.py
scripts/validate_final_upgrade_regression.py
tests/test_final_upgrade_regression_a54.py
.github/workflows/a20-release-candidate.yml
```

Representative matrix:

```text
Nova     fintech/trust/data        e206f51f2fda006adcf52497d8b827e048e157ec
Lumen    visual/cultural           219f3e49f9956290ef69a2e49cb91fefddd5f561
CENNEXT  B2B/enterprise            273403accf8979608fbb16dbe2741cedb0430fb6
LuxRoom  ecommerce/purchase flow   37e6a8c4a2aecdb9cefd9fd4291b353252d5356b
```

Repository-only CI intentionally holds because real project receipts are absent:

```text
HOLD_FINAL_REGRESSION_EVIDENCE_REQUIRED
```

A20 checks out all four exact SHAs, runs the generic real-project lane, runs structural/security regression, and aggregates:

```text
release-audit.json
nova-generic.json
lumen-generic.json
cennext-generic.json
luxroom-generic.json
flow4-final.json
```

Required final result:

```text
WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS
projects = 4 / 4
release_audit_passed = true
flow3_clear = true
contract_clear = true
governance_boundary_clear = true
```

Each generic project report must retain:

```text
browser.status = NOT_RUN
provider_reasoning.status = NOT_RUN
human_review.status = pending
human_review.verdict = null
release.status = NOT_ATTEMPTED
```

This prevents cross-project dogfood from manufacturing browser, provider-quality, human-review, deploy or release evidence.

## 11. Flow 5 final owner review and upgrade closure

Executable owner set:

```text
benchmarks/final-owner-review-closure-v1.json
core/benchmarks/final_owner_review_closure.py
scripts/validate_final_owner_review_closure.py
tests/test_final_owner_review_closure_a55.py
.github/workflows/uiux-factory-ci.yml
.github/workflows/a20-release-candidate.yml
```

Repository-only CI intentionally derives:

```text
HOLD_FINAL_OWNER_REVIEW_EVIDENCE_REQUIRED
```

because the real `flow4-final.json` receipt exists only in the A20 evidence lane. A20 feeds that exact Flow 4 receipt into Flow 5 and cross-checks all four project IDs/SHAs, Flow 3 ledger truth, the five hold triggers, owner delegation, repository-hygiene receipt and every non-authority boundary.

Proven A20 closure state:

```text
WORKSPACE_UPGRADE_CLOSED_WITH_INTENTIONAL_HOLDS
flow3_clear = true
flow4_contract_clear = true
flow4_report_present = true
flow4_clear = true
intentional_holds_preserved = true
owner_delegation_clear = true
owner_review_source_clear = true
repository_hygiene_receipt_clear = true
governance_boundary_clear = true
final_owner_review_completed = true
upgrade_closed = true
future_hold_triggers_preserved = true
independent_human_review_claimed = false
```

The five intentional holds remain active and non-blocking for this closed upgrade. Closure does not grant provider migration, lifecycle unification, GenAI promotion, vector retrieval activation or compatibility-wrapper deletion.

## 12. Regression surfaces

Active regression owners include:

```text
uiux-factory/benchmarks/corpus/
uiux-factory/benchmarks/routing-v1.json
uiux-factory/benchmarks/repair-proposals-v1.json
uiux-factory/benchmarks/memory-boundary-v1.json
uiux-factory/benchmarks/scorecard-v1.json
uiux-factory/benchmarks/provider-parity-v1.json
uiux-factory/benchmarks/provider-default-migration-readiness-v1.json
uiux-factory/benchmarks/lifecycle-parity-v1.json
uiux-factory/benchmarks/lifecycle-mutation-convergence-readiness-v1.json
uiux-factory/benchmarks/lifecycle-event-interop-v1.json
uiux-factory/benchmarks/runtime-compatibility-convergence-v1.json
uiux-factory/benchmarks/compatibility-surface-governance-v1.json
uiux-factory/benchmarks/architecture-debt-closure-audit-v1.json
uiux-factory/benchmarks/final-upgrade-regression-v1.json
uiux-factory/benchmarks/final-owner-review-closure-v1.json
.github/workflows/uiux-factory-ci.yml
.github/workflows/a20-release-candidate.yml
```

UIUX Factory CI owns repository-local regression and fail-closed contract validation. A20 owns pinned real-project final evidence and the resulting Flow 5 closure receipt.

## 13. Standing owner delegation

Current delegation artifact:

```text
uiux-factory/benchmarks/governance-owner-delegation-v1.json
```

Mandatory failures cannot be bypassed. Independent-human evidence cannot be fabricated. Protected history, secrets and permissions remain outside delegated continuation. The delegation artifact retains the historical requirement for a final retrospective owner review; Flow 5's closure receipt records that the owner-governance review completed after Flow 4 evidence became valid.

## 14. Upgrade closure boundary

Current bounded upgrade decision:

```text
WORKSPACE_UPGRADE_CLOSED_WITH_INTENTIONAL_HOLDS
```

There is no next numbered task in this upgrade sequence. Future work begins only from a new owner product/architecture goal or an explicit hold trigger with its required evidence.

The five holds remain:

```text
provider_default_migration
lifecycle_mutation_convergence
genai_nist_expansion
vector_semantic_retrieval
compatibility_surface_removal
```

They are not silently cleared by upgrade closure and must not be treated as permission for automatic mutation.

## 15. Post-closure Productization / Reliability Hardening

Post-closure P0–P4 improve real-world use without reopening A50–A55 or granting new authority.

### P0 — target-truth-aware routing

Current external-task routing path:

```text
checked-out target repository
→ TargetTruthProbe

current task text
→ GoalInterpreter

TargetTruthProbe + GoalInterpreter
→ truth-aware Task Contract
→ explicit caller overrides
→ final contract coherence
→ FlowPlanner
```

Canonical owners:

```text
core/runtime/flow_os/target_truth.py
core/runtime/flow_os/external_task.py
skills_UIUX/scripts/github-external-agent-runner.py
skills_UIUX/scripts/prepare-external-task.py
```

Routing precedence is:

```text
explicit caller override
> structured target-project truth
> natural-language goal inference
```

Target truth is bounded to routing metadata only:

```text
website_type
domain
product_archetype
validation_lane
mode
risk
features
```

It cannot grant provider/model selection, gate/evidence verdicts, merge/deploy permission, release authorization or any other authority. Target-truth provenance records authority/evidence/release effects as `none`.

Structured project truth is read from `.uiux-profile.json` and project-context files before fallback metadata. README/package metadata remains fallback-only and cannot overwrite a stronger specific task identity.

### P1 — protected-main server-side governance

GitHub repository ruleset `Protect main` is active for the default branch. Normal changes to `main` require a pull request plus exact-head GitHub Actions checks:

```text
foundation
release-candidate
```

The ruleset requires the branch to be up to date and blocks deletion/non-fast-forward force pushes. Routine bypass actors are not part of the normal owner/developer path. This is server-side repository governance, not runtime authority.

### P2 — public presentation/evidence hygiene

Public guidance uses `scenario-based expert walkthroughs` / `simulated usage scenarios` rather than synthetic-user framing that could be mistaken for participant research. Superseded planning material lives under `docs/history/`; the root README exposes current architecture/evidence boundaries without claiming that CI proves visual quality, human preference, product impact or release readiness.

### P3 — target-truth size reliability + truth sync

`TargetTruthProbe` detects source overflow by reading at most `MAX_SOURCE_CHARS + 1` characters:

```text
.uiux-profile.json oversized
→ fail closed with explicit size-limit error
→ never truncate structured JSON and misreport it as malformed

package.json oversized fallback
→ ignore with explicit oversized-fallback diagnostic

README / project-context unstructured text
→ bounded truncation remains allowed
```

Malformed in-limit `.uiux-profile.json` still fails closed as malformed. Symlink escape protection, routing precedence and all non-authority boundaries remain unchanged.

### P4 — target-truth cross-field coherence + contradiction hardening

Target identity is now checked as a coherent set before fallback metadata can influence Flow planning. Canonical domain-bound archetypes owned by Flow OS carry an explicit required-domain relation; currently this applies to the existing financial archetypes.

```text
structured domain + domain-bound archetype agree
→ accept

structured domain + domain-bound archetype contradict
→ fail closed with TargetTruthProbeError
→ include domain/archetype source provenance in the diagnostic

domain-bound structured archetype + missing domain
→ derive its required domain
→ provenance remains non-authoritative

structured domain + conflicting fallback archetype
→ drop the fallback archetype
→ emit ignored_incoherent_fallback diagnostic
```

P4 does not turn arbitrary custom archetype slugs into domain authority. It only binds archetypes for which Flow OS already owns a canonical domain requirement. Derived target truth still has authority/evidence/release effects `none`.

P0–P4 do not clear or weaken any of the five A55 intentional holds.

## 16. Future convergence rules

Future work must preserve:

```text
Brain OS reasoning/control
→ canonical task interpretation / Flow OS planning
→ Factory manager or ManagedFlowController
→ specialist execution / tools
→ existing evidence + QA
→ canonical evaluation
→ advisory memory/scorecard/knowledge
```

It must not create a third runtime/provider-policy abstraction, treat observation receipts as shared mutation state, let advisory channels satisfy runtime gates, infer external compatibility safety from zero internal consumers, or clear explicit holds without their required evidence.