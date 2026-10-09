# UIUX Factory — START HERE

This is the shortest safe entrypoint for humans and external AI collaborators.

## If the user gives a goal + target repository

Do **not** read the whole workspace.

1. Read `AGENTS.md` for the universal operating/evidence contract.
2. Read `docs/CONTRACT-OWNERSHIP.md` to know which file owns which decision.
3. Build or recover one `external-task-manifest.json`. When a checked-out target is available, pass its root so bounded project truth is probed **before** Flow resolution. If the collaborator cannot run the local CLI or dispatch Actions directly, use the bounded GitHub-connector ingress described below instead of manually re-implementing the routing logic.
4. Load only the resolved Flow and the `SKILL.md` files listed for the **active stage**.
5. Audit the target repository before editing it; project source is stronger evidence than filename assumptions.
6. Work on a branch, verify with direct evidence, repair root causes, then open/merge a PR only when the relevant gates pass.

```bash
python -B skills_UIUX/scripts/prepare-external-task.py \
  --repository owner/repo \
  --target-root /path/to/checked-out-project \
  --task "Redesign the portfolio toward Product Designer and make AI workflow evidence inspectable" \
  --authority branch_write \
  --output external-task-manifest.json
```

`--target-root` is optional for the lightweight CLI. If it is omitted, the manifest records `target_truth.status = NOT_PROVIDED` and routes from task inference rather than pretending target truth was inspected. The GitHub-native runner always passes its checked-out target root.

The manifest is a **routing contract**, not proof that the target project passed QA. Its initial status is always `READY_FOR_EXTERNAL_COLLABORATOR`.

## Target-truth-aware routing

When a checked-out target exists, routing uses this bounded pipeline:

```text
TargetTruthProbe + GoalInterpreter
→ truth-aware Task Contract
→ explicit caller overrides
→ final contract coherence
→ FlowPlanner
```

The declared precedence is:

```text
explicit override > structured target-project truth > natural-language goal inference
```

The merge is conservative rather than a blind overlay. Structured project identity can correct generic task inference; project lifecycle metadata acts as a default and does not erase a stronger lifecycle request in the current task; README/package metadata is fallback-only. The final manifest records `target_truth` plus `routing_provenance` so every applied routing field is inspectable.

Target truth is routing context only. It can contribute `website_type`, `domain`, `product_archetype`, `validation_lane`, `mode`, `risk` and known `features`. It cannot grant authority, provider selection, gate PASS, evidence status, merge permission, deploy permission or release authority. A project file saying `merge_and_deploy` therefore cannot escalate the collaborator.

Canonical implementation: `uiux-factory/core/runtime/flow_os/target_truth.py`. Post-closure design note: `uiux-factory/docs/architecture/POST-CLOSURE-P0-TARGET-TRUTH-ROUTING.md`.

## Context loading rule

Use progressive disclosure:

```text
START-HERE.md
→ AGENTS.md
→ docs/CONTRACT-OWNERSHIP.md
→ external-task-manifest.json
→ one resolved flow document
→ only active-stage SKILL.md files
→ target-repository source/evidence
```

Do not preload old A-series design notes, every skill, every flow, or every runtime document. They are historical/implementation context unless the active task specifically needs them.

Machine-readable loading profiles live in `skills_UIUX/runtime/context-routing.json`.

For active visual-design work, the stage packet now includes `design_workflow`: use structured project identity + one page-role lookup, then record adopted numeric/media/composition decisions and run its canonical integrity checker. A SKILL.md name in the packet is not proof the resource was retrieved or applied. The decision owner is `skills_UIUX/visual-design-direction/SKILL.md`; load its resources only for the current decision. Technical/contract PASS never proves aesthetic quality.

New design contracts use v2: retrieve domain/page-role reference anatomy, explain each transfer, compare materially different free typography/density/object axes, and predeclare comprehension/distinctiveness questions. Use the comparison CLI or routed read-only provider tools to prepare labelled reviews and summarize capture-bound observations. Legacy v1 remains inspectable as layout-only evidence and cannot satisfy a v2 gate. Human participation and causal improvement remain UNKNOWN until appropriate evidence exists.

## External model-selection preflight

For ChatGPT, Codex, Claude or another consumer UI where the model is selected manually before execution, the Factory exposes an advisory preflight instead of pretending it can switch the consumer model mid-run:

```bash
python -B skills_UIUX/scripts/advise-external-task.py \
  --repository owner/repo \
  --task "Review provider truth, read-only permissions and regression risk"
```

The result recommends a provider-neutral capability tier (`efficient`, `balanced`, or `advanced`), reasoning effort, context strategy and checkpoint/resume guidance. The human still selects the actual model. The advisor cannot grant authority, satisfy gates, authorize paid-provider use, or become QA evidence. See `docs/ADAPTIVE-COMPUTE-AND-MODEL-SELECTION.md`.

## Canonical execution surfaces

- Target-project routing truth: `uiux-factory/core/runtime/flow_os/target_truth.py`
- External/cloud collaborator: `skills_UIUX/scripts/prepare-external-task.py`
- GitHub-native external collaborator control plane: `.github/workflows/external-agent-runner.yml`
- GitHub connector ingress when direct Actions dispatch is unavailable: `.github/workflows/external-agent-connector-bridge.yml` + `skills_UIUX/scripts/github-connector-task-request.py`
- Managed local/provider Flow OS: `skills_UIUX/scripts/uiux-agent.py`
- Direct Factory pipeline: `uiux-factory/run.py`
- Browser/accessibility/performance evidence: `uiux-factory/qa/`
- Lifecycle State Coverage + semantic assertions + rendered matrix: `uiux-factory/qa/scripts/state-coverage.mjs`
- Infra/release failure taxonomy: `uiux-factory/qa/scripts/infra-failure-classifier.mjs`
- Deployment truth: `uiux-factory/qa/scripts/deployment-truth.mjs` + `.github/workflows/deployment-truth-gate.yml`
- Release evidence registry: `uiux-factory/core/provenance/release_evidence_registry.py` + `skills_UIUX/scripts/build-release-evidence.py`
- Flow definitions: `skills_UIUX/flows/*.json`
- Skill capabilities: `skills_UIUX/<skill>/SKILL.md`

## GitHub-native external collaborators

When ChatGPT, Codex, Claude or another external collaborator can work through GitHub but cannot execute the Factory locally, prefer the canonical `GitHub Native External Agent Runner` from Actions (or call it as a reusable workflow). It checks out the exact target ref, probes bounded routing truth from that checkout, compiles the governed task packet, records target SHA/source evidence, and can optionally run the State Coverage Gate when the target declares a contract.

If the connected GitHub client can create/edit issues but cannot invoke `workflow_dispatch`, use the **GitHub Connector External Agent Bridge**. Create a trusted issue titled with the `[UIUX TASK]` prefix (or apply the `uiux-agent-task` label) and include this marker plus a JSON payload:

````markdown
<!-- uiux-external-agent-task:v1 -->
```json
{
  "target_repository": "owner/repo",
  "target_ref": "main",
  "task": "Improve the existing dashboard cards while preserving current motion",
  "authority": "branch_write",
  "qa_routes": ["/"],
  "acceptance": ["No layout overflow", "Rendered QA required"],
  "state_contract": "uiux-state-coverage.json"
}
```
````

The bridge accepts **metadata only**. It intentionally rejects unknown fields such as `install_command`, `build_command` and `serve_command`, so issue text cannot create an arbitrary shell-execution path. The workflow validates the request, checks out the target repository, reuses `github-external-agent-runner.py`, uploads the governed packet as an artifact, and comments the run location on the issue. Private cross-repository targets may still require the repository secret `UIUX_TARGET_REPO_TOKEN`, the same trust boundary used by the existing runner.

The runner and connector bridge do **not** pretend to invoke an LLM provider. They create the governed GitHub-native control plane around the external collaborator. Implementation still happens through the authorized collaborator; runtime/visual PASS still requires target evidence.

Lifecycle-state projects can declare `uiux-state-coverage.json` (or another contract path) to verify state query → semantic marker → rendered evidence across desktop/tablet/mobile and automatically generate a 2×2 case-study matrix. See `docs/STATE-COVERAGE-INFRASTRUCTURE.md`.

## Visual-signature routing

The external-task manifest automatically adds `docs/VISUAL-SIGNATURE-REGRESSION-CONTRACT.md` to `canonical_sources` when the interpreted task can modify an existing rendered UI or otherwise declares a compatibility boundary. New builds and explicitly authorized full redesigns do not load that contract by default; preserve/forbidden constraints reactivate it. This keeps context small without silently dropping protection for existing visual identity.

## Release proof

A merged PR or green build is not release proof. Use A35 Deployment Truth when a release claim matters. `DEPLOYED_VERIFIED` requires the intended release SHA, provider-reported deployment SHA, a ready deployment status and a 2xx production route observation. Provider capacity/auth failures stay separate from product QA. See `docs/DEPLOYMENT-TRUTH.md`.

Use A36 Release Evidence Registry to produce one integrity-hashed `uiux-evidence-manifest.json` that references task/source/browser/state/deployment artifacts without replacing their originating evidence owners. Missing evidence remains `UNKNOWN`. See `docs/EVIDENCE-REGISTRY.md`.

A37 dogfoods these surfaces together against pinned CENNEXT target truth. It intentionally refuses to claim a verified deployment when trusted provider SHA metadata is absent. See `docs/A37-REAL-PROJECT-E2E-DOGFOOD.md`.

## Pre-design research

Explicit buyer/reference research before design routes the `pre-design-research` feature (or pass `--feature pre-design-research`). Research-only stays in `audit-review`; substantial build/redesign keeps its own research stage. Stage `research_workflow` links decision-led methods, anatomy and synthesis; `research_packet` retains its human-study contract. Desk findings may be real evidence without human sessions. Read the [working flow and evidence boundaries](docs/PRE-DESIGN-RESEARCH.md).

## Human research

When a task needs real-user evidence, activate `research-evidence-pipeline` plus the existing research skills. If participant access does not exist, produce a plan/package and label the state `PLANNED_VALIDATION`, `BLOCKED_USER_EVIDENCE`, or `UNKNOWN`. Never invent sessions, quotes, counts, percentages or findings.

## Portfolio/career work

Full portfolio rebuilds and role-positioning upgrades route to `portfolio-career-system` when the task contract identifies `website_type=portfolio` and a REDESIGN/PRODUCT-sized surface. Target-project truth may supply the portfolio identity even when the current task text is terse. The flow covers recruiter narrative, identity/CV/link consistency, evidence boundaries, case-study product reasoning, technical proof, rendered QA, and research gaps.

## Completion rule

A task is complete only when the requested scope and relevant gates have evidence. Build success, provider self-report, a generated manifest, or a green fixture are never substitutes for target-project verification.
