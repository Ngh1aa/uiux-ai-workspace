# UIUX Factory — START HERE

This is the shortest safe entrypoint for humans and external AI collaborators.

## If the user gives a goal + target repository

Do **not** read the whole workspace.

1. Read `AGENTS.md` for the universal operating/evidence contract.
2. Read `docs/CONTRACT-OWNERSHIP.md` to know which file owns which decision.
3. Build or recover one `external-task-manifest.json` using the command below, or follow its schema manually when the collaborator cannot execute the local CLI.
4. Load only the resolved Flow and the `SKILL.md` files listed for the **active stage**.
5. Audit the target repository before editing it; project source is stronger evidence than filename assumptions.
6. Work on a branch, verify with direct evidence, repair root causes, then open/merge a PR only when the relevant gates pass.

```bash
python -B skills_UIUX/scripts/prepare-external-task.py \
  --repository owner/repo \
  --task "Redesign the portfolio toward Product Designer and make AI workflow evidence inspectable" \
  --authority branch_write \
  --output external-task-manifest.json
```

The manifest is a **routing contract**, not proof that the target project passed QA. Its initial status is always `READY_FOR_EXTERNAL_COLLABORATOR`.

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

## Canonical execution surfaces

- External/cloud collaborator: `skills_UIUX/scripts/prepare-external-task.py`
- GitHub-native external collaborator control plane: `.github/workflows/external-agent-runner.yml`
- Managed local/provider Flow OS: `skills_UIUX/scripts/uiux-agent.py`
- Direct Factory pipeline: `uiux-factory/run.py`
- Browser/accessibility/performance evidence: `uiux-factory/qa/`
- Lifecycle State Coverage + semantic assertions + rendered matrix: `uiux-factory/qa/scripts/state-coverage.mjs`
- Infra/release failure taxonomy: `uiux-factory/qa/scripts/infra-failure-classifier.mjs`
- Flow definitions: `skills_UIUX/flows/*.json`
- Skill capabilities: `skills_UIUX/<skill>/SKILL.md`

## GitHub-native external collaborators

When ChatGPT, Codex, Claude or another external collaborator can work through GitHub but cannot execute the Factory locally, use `GitHub Native External Agent Runner` from Actions (or call it as a reusable workflow). It checks out the exact target ref, compiles the governed task packet, records target SHA/source evidence, and can optionally run the State Coverage Gate when the target declares a contract.

The workflow does **not** pretend to invoke an LLM provider. It creates the governed GitHub-native control plane around the external collaborator. Implementation still happens through the authorized collaborator; runtime/visual PASS still requires target evidence.

Lifecycle-state projects can declare `uiux-state-coverage.json` (or another contract path) to verify state query → semantic marker → rendered evidence across desktop/tablet/mobile and automatically generate a 2×2 case-study matrix. See `docs/STATE-COVERAGE-INFRASTRUCTURE.md`.

## Human research

When a task needs real-user evidence, activate `research-evidence-pipeline` plus the existing research skills. If participant access does not exist, produce a plan/package and label the state `PLANNED_VALIDATION`, `BLOCKED_USER_EVIDENCE`, or `UNKNOWN`. Never invent sessions, quotes, counts, percentages, or findings.

## Portfolio/career work

Full portfolio rebuilds and role-positioning upgrades route to `portfolio-career-system` when the task contract identifies `website_type=portfolio` and a REDESIGN/PRODUCT-sized surface. The flow covers recruiter narrative, identity/CV/link consistency, evidence boundaries, case-study product reasoning, technical proof, rendered QA, and research gaps.

## Completion rule

A task is complete only when the requested scope and relevant gates have evidence. Build success, provider self-report, a generated manifest, or a green fixture are never substitutes for target-project verification.
