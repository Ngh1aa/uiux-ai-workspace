# Default Website Delivery Policy — Adaptive Prompt OS V4

This file defines the default website-delivery operating policy for projects that use `skills_UIUX`.

Canonical policy ID:

```text
adaptive-prompt-os-v4
```

The policy is stack-agnostic and domain-aware. Project truth and routed domain skills decide the actual design; this policy decides the default delivery discipline.

## Adaptive lane selection

Do not run the full lifecycle mechanically for every tiny edit.

### Full Prompt OS lane — default for substantial website work

Use the full lane for new websites, major rebuilds, substantial redesigns, multi-page/whole-site changes, critical journey redesigns, new page families that materially change IA/composition, design-system/art-direction resets, and production-level releases with meaningful UI/UX change.

```text
PROMPT 0 — PROJECT CONFIG
→ PROMPT 1 — RESEARCH / AUDIT / DESIGN CONTRACT
→ PHASE 1 PASS
→ PROMPT 2 — STRUCTURAL IMPLEMENTATION
→ REPRESENTATIVE PAGE GATE
→ WHOLE-SCOPE ROLLOUT
→ PROMPT 3 — FINAL QA + REMEDIATION
→ HUMAN VISUAL VETO
→ FINAL QA PASS
→ PROMPT 4 — RELEASE + PRODUCTION SMOKE, ONLY WHEN AUTHORIZED
```

### Lightweight lane — default for bounded local work

Use the lightweight lane for genuinely local/component-level low-risk changes that do not alter structural design direction.

```text
project truth
→ classify scope/type/risk/mode
→ smallest applicable skill graph
→ inspect root owner
→ focused implementation
→ focused rendered/browser verification
→ affected shared-owner regression
→ release only when authorized
```

Escalate lightweight work when the root cause becomes shared, structural, cross-route, art-direction, production/high-risk or otherwise material.

## Prompt 0 — Project Config

Resolve project/repository, request type, mode, domain/audience when known, business/product goal, critical journeys, must-keep/must-improve, responsive scope, source of truth, release authorization, system-reality boundaries, and immutable skills version lock. Unknown facts remain UNKNOWN.

## Prompt 1 — Research, Audit and Design Contract

No broad implementation before this phase passes for substantial website work.

Account for the current site/new-site baseline, audience/tasks/journeys, IA/page roles, reference benchmark, focused design intelligence when useful, ADOPT/ADAPT/REJECT synthesis, structural redesign delta, visual direction, media/focal contract when material, Design Contract, representative composition proofs, requirement coverage and verification plan.

A substantial redesign does not pass when the planned delta is primarily color, typography, spacing, radius, shadow, gradient, animation or image replacement inside the same hierarchy/composition/journey.

## Prompt 2 — Structural Implementation

Default implementation order:

```text
composition
→ hierarchy
→ media
→ decision/task objects
→ interaction and states
→ declared responsive transformation
→ system/component consolidation
→ visual polish
```

For multi-page/journey/whole-site work, implement and render 2–4 representative surfaces selected from the actual sitemap/page-role matrix/critical journeys/risk before broad rollout. Fix P0/P1 issues first.

## Prompt 3 — Final QA and Remediation

Verify critical journeys, page-role diversity, shared-owner visual sanity, media crop/load integrity, declared responsive behavior, accessibility baseline, system-reality truthfulness, runtime errors, overflow, preserved behavior and brand consistency.

Build success is not rendered evidence. A screenshot that exists but was not opened is not visual evidence. An obviously wrong screenshot fails even when automated QA says 100/100.

Human/Creative-Director verdicts:

```text
KEEP
REVISE
REMOVE
```

Material REVISE/REMOVE feedback returns to the owning stage and must be re-rendered after repair.

## Prompt 4 — Release and Production Smoke

Run only when release is authorized:

```text
no_release
create_pr_only
merge_only
merge_and_deploy
```

When deployment occurs, deploy success is not final proof. Verify the real served version, cache-busted assets, production URL, representative routes, critical journey entry points, stylesheet/font/image/media loading, console/network/runtime sanity and stale-build risk.

## Non-negotiable truth rules

System reality:

```text
REAL | MOCK | STATIC | SIMULATED | PARTIAL | UNKNOWN
```

Requirement states:

```text
DONE_VERIFIED
N/A_JUSTIFIED
PENDING_FUTURE_PHASE
BLOCKED
```

Only due-now requirements participate in the current phase exit gate. Future evidence gets an owner phase + verification plan.

## Creative Director rule

For substantial visual work, rendered evidence must be inspected after the latest material visual change. Final taste review covers hierarchy, composition, brand distinctiveness, image/media coherence, page-role diversity, generic-template risk, and whether the intended brand/product feeling is actually visible.

Factory/process owns repeatable orchestration and deterministic gates. Routed skills own specialist rules. Creative Director review owns final visual judgment.

## Project override rules

Precedence:

```text
current user request
→ project .uiux-profile.json / project truth
→ passed project Design Contract
→ this default policy
→ routed specialist skills
→ generic model prior
```

Project overrides may change lane, responsive scope, mode and release authorization when justified, but must not silently weaken system-reality honesty, evidence discipline, release authorization or rendered-inspection requirements.

Machine-readable contract:

```text
policies/adaptive-prompt-os-v4.json
```

Canonical supporting documents:

```text
PROJECT-INSTRUCTIONS-PHASE-AWARE.md
PHASE-AWARE-GATING.md
LATEST-3-PROMPT-REDESIGN-PIPELINE.md
MASTER-PRE-DESIGN-RESEARCH-PROMPT-V4.2.md
MASTER-PROMPT-V7.2.md
FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V3.2.md
website-delivery-pipeline/SKILL.md
adaptive-skill-routing-and-context-budget/SKILL.md
project-context/SKILL.md
```
