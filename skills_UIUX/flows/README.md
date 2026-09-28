# Declarative Flows

`flows/*.json` is the routing layer between a natural-language Task Contract, specialist agent roles and `SKILL.md` capabilities.

```text
task goal
→ canonical GoalInterpreter
→ FlowResolver
→ resolved Flow
→ active stage agent
→ SkillResolver(role defaults + required + conditional/JIT)
→ gate evidence
→ PASS: advance | failure/risk: bounded ReplanningEngine
```

The universal behavior/evidence policy belongs to `AGENTS.md`; authority/provider/sandbox/release policy belongs to `runtime/runtime-policy.json`; specialist guidance belongs to each `SKILL.md`. Flows should reference capabilities rather than copy their knowledge. See `docs/CONTRACT-OWNERSHIP.md`.

## Active flow families

- `micro-ui-change` — atomic visual/component edits.
- `existing-ui-improvement` — focused fixes/improvements to existing UI surfaces.
- `page-ui-work` — page/route-sized work.
- `professional-website-redesign` — broad professional website/product build/rebuild/redesign.
- `portfolio-career-system` — broad portfolio/career-positioning work where recruiter narrative, case evidence, CV/identity/link hygiene, AI workflow proof and source claims must be evaluated together.

`portfolio-career-system` has higher specificity/priority for portfolio + PRODUCT/REDESIGN surfaces. A narrow portfolio request such as “fix the hero” remains focused and does not invoke the full career system.

## Task context

The manager routes on:

- `intent`: build/redesign/rebuild/improve/fix/polish;
- `change_surface`: MICRO/FOCUSED/PAGE/REDESIGN/PRODUCT;
- `website_type`: corporate, ecommerce, education, government, hospitality, news, real-estate, saas, startup, portfolio, nonprofit, landing, generic/future types;
- `domain` and `product_archetype` when evidence supports them;
- `validation_lane`: prototype, evidence-led, production-learning;
- `mode`: visual-prototype, interactive-prototype, production-candidate, production;
- `risk`;
- `features`: auth/forms/search/dashboard/motion/i18n plus lifecycle signals such as user-validation or outcome-measurement.

Flow matching stays intentionally small. Detail belongs in conditional skill routing rather than a giant manager prompt.

## Stage contract

Each stage declares:

- `id` and owning agent role;
- purpose;
- required skills;
- conditional skills driven by task context;
- gates;
- optional approval;
- bounded replanning behavior at flow level.

Role defaults and flow-required skills are mandatory. The Development Manager executes only the active stage and blocks stage skipping.

## Evidence-led research

Flows may route `real-user-validation`, `user-research-planning-and-recruitment`, `research-synthesis-and-insight-management` and/or the operational `research-evidence-pipeline`.

The canonical pipeline provides reusable plan/screener/interview/usability/ledger templates. A research protocol is not research evidence. If participants or production behavior are unavailable, keep the state PLANNED/BLOCKED/UNKNOWN rather than manufacturing findings.

## External collaborator manifest

`skills_UIUX/scripts/prepare-external-task.py` resolves the same Task Contract + Flow stack for ChatGPT/Codex/Claude or another external collaborator and emits `external-task-manifest.json` containing exact stage skills, gates, acceptance criteria, QA routes and evidence boundaries.

A manifest is routing evidence only. Target implementation/browser/test evidence is still required for completion claims.

## Replanning

Replanning is **not retry**. An applied replan:

- originates from an explicit configured signal;
- respects the remaining replan budget;
- targets an allowed stage;
- may add/drop only legal non-mandatory skills;
- increments the flow revision;
- invalidates only affected downstream completion;
- never grants higher authority.

## Validation

When adding/editing a flow run:

```bash
python -B skills_UIUX/scripts/validate-flows.py
python -B skills_UIUX/scripts/validate-runtime-foundation.py
```

The portable schema is `skills_UIUX/schemas/flow.schema.json`. Runtime enforcement remains dependency-free in the canonical Flow OS implementation.
