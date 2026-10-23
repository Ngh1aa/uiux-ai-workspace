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

Skill source maintenance uses `skill-library-maintenance`; explicit read-only review
uses `skill-library-audit`. Both reuse the existing research/implementation/QA roles
and `skill-authoring-and-governance`. Their scoped feature does not activate for an
ordinary website teaching skills. UI specimens still need rendered review when
visual claims are made; source maintenance does not manufacture frontend work.

Mobile browser prototypes use `mobile-web-preview` (research/design/implementation/qa) with `requested_output=browser-prototype`; website flows are reused only for their browser skills/evidence, not native implementation. Publication is separate authorized work and a prepared packet is not a live client URL. Mobile design uses `mobile-app-design` (research/design/qa) and `mobile-app-audit` (read-only research/qa). `platform_family=mobile_app` must be explicit or supported by bounded goal/target truth; `requested_output=design` preserves the design-only scope. Unannotated flows retain web semantics. Native code requests do not fall back to a web flow. See [mobile practice](../mobile-app-design/references/professional-practice.md).

- `micro-ui-change` — atomic visual/component edits.
- `existing-ui-improvement` — focused fixes/improvements to existing UI surfaces.
- `page-ui-work` — page/route-sized work.
- `professional-website-redesign` — broad professional website/product build/rebuild/redesign.
- `design-system-work` — create, extend or refactor a design system when the system itself is the work object (feature `design-system`); `design-system-audit` is its read-only twin. Applying an existing design system to a page does not trigger it.
- `web-app-dashboard` — dashboards, admin consoles, back-office and internal tools when the dashboard is the work object (feature `app-dashboard`); a product build that merely includes a dashboard keeps the broader flow, and MICRO/FOCUSED edits keep their small lanes.
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
