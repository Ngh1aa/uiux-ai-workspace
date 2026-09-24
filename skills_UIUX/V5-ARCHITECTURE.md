# skills_UIUX V5 Architecture — Evidence, Reference Intelligence, Measurement & Production Reliability

V5 adds five coordinated layers on top of the existing UX/UI/domain foundation:

1. **Evidence & measurement** — claims, outcomes, conformance and reliability must be evidence-backed.
2. **Reference intelligence** — major visual direction can learn from real/curated references without copying or treating awards as UX proof.
3. **Real-world artifact intelligence** — domain objects, documents, environments and rituals can inform mental-model-aligned digital structure and distinctive design grammar without literal skeuomorphic imitation.
4. **Production reality** — rendered UI must not be confused with real integrations/data/behavior.
5. **Delivery reliability** — proportional planning, verification, safe release/rollback and production feedback.

It does not replace V4 audience/experience strategy, V3 research/advanced UX, or domain playbooks.

## Core idea

`project truth → evidence → audience/intent → journey/IA → digital reference intelligence + domain artifact intelligence → brand/system → system reality/data contract → plan → implementation → verification → release → real outcomes → continuous learning`

## Why V5 exists

A strong framework can still fail if:

- research/user claims cannot be traced to a source;
- a prettier redesign is called an UX improvement without outcome data;
- an award/gallery reference is treated as proof of usability/conversion;
- a generic card/template system ignores strong domain objects and mental models that could create more intuitive/distinctive structure;
- a physical metaphor is copied too literally and becomes decorative skeuomorphism or misrepresents a real product;
- accessibility is claimed from automated scans or spot checks;
- visual/design-system drift accumulates;
- every task loads too much context;
- UI success states imply backend success that does not exist;
- mock/static data ships as if it were live;
- CI/build/Lighthouse green is mistaken for production verification;
- release rollback relies on destructive history rewriting;
- an agent passes once and is called reliable;
- production feedback never becomes research/tests/regression coverage.

## Progressive disclosure

V5 deliberately keeps the master orchestrator smaller than a monolithic mega-prompt:

`orchestrator → specialist SKILL.md → references/checklists/examples only when decision is active`

This reduces context dilution and keeps project truth visible.

## Capability packs

### `measurement-reliability`

1. `evidence-provenance-and-research-ops`
2. `journey-outcome-and-service-health`
3. `brand-recognition-validation`
4. `accessibility-conformance-evaluation`
5. `visual-regression-and-design-drift`
6. `adaptive-skill-routing-and-context-budget`
7. `agent-evaluation-and-reliability`
8. `continuous-learning-and-improvement`

Use when substantial outcome/conformance/regression/reliability claims need stronger evidence.

### `production-delivery`

1. `system-reality-and-production-readiness`
2. `ai-agent-coding-guardrails`
3. `security-and-privacy`
4. `web-quality-and-performance`
5. `testing-strategy`
6. `code-review-and-release`
7. `production-monitoring-and-maintenance`

Use for production-candidate/release work where real integrations, data truth, security, browser/performance verification, rollback or post-release health are material.

Do not load either whole pack for a tiny low-risk style fix.

## Reference-intelligence contract

`project/domain context → source mix → candidate pool → fit scoring → finalists by role → principle extraction → project adaptation → visual/system handoff`

Rules:

- real production/category sites are stronger evidence for IA/journey/trust/conversion patterns;
- curated/award sources are strong visual-craft input but not automatic UX proof;
- case-study/shot/mood sources have explicit secondary roles;
- label production vs concept/unknown when material;
- extract Design DNA/rules, not branded surface/assets.

## Real-world artifact-intelligence contract

Use `real-world-artifact-and-domain-metaphor-design` when domain-native objects, documents, spatial systems or rituals can materially improve recognition, information structure, journey logic or brand distinctiveness.

Pipeline:

`design problem → domain artifact inventory → artifact anatomy/behavior → transfer layer → fidelity L0–L4 → keep/do-not-copy → brand/mobile/a11y/performance adaptation → system handoff`

Five transfer layers:

1. **form** — geometry/proportion;
2. **structural** — layout/information composition;
3. **information** — object attributes/relationships/actions;
4. **behavioral** — familiar interaction where it predicts digital behavior;
5. **ritual/process** — offline service logic adapted to digital.

Fidelity ladder:

`L0 REFERENCE_ONLY | L1 CUE | L2 STRUCTURAL | L3 DIRECT_FORM | L4 IMMERSIVE`

Core rules:

- default to the lowest metaphor fidelity that communicates the idea;
- familiarity is useful only when expected meaning/behavior remains predictable;
- do not carry unnecessary physical-world friction into digital;
- real branded products/official documents must use verified current assets/specs or be labeled representative/concept/unknown;
- accessibility/semantics cannot depend on recognizing the visual metaphor;
- a page/system should synthesize a coherent domain grammar rather than become a collage of clever artifacts.

This layer complements `design-reference-research-and-benchmark`, then hands off to `brand-distinctiveness-and-visual-signature`, `visual-design-direction` and `design-system-and-components`.

## System-reality contract

Material capabilities can be labeled:

`REAL | MOCK | STATIC | SIMULATED | PARTIAL | UNKNOWN`

Rules:

- rendered success state is not proof of backend success;
- search/login/checkout/CMS/analytics UI is not proof of real integration;
- dynamic features need data/API/state contracts when production-relevant;
- production gaps need severity/dependency/owner;
- `REAL/working/integrated/production-ready` require evidence appropriate to the exact claim.

## Implementation contract

Substantial/high-risk work should use proportional planning:

`goal → owning files/components → dependencies → expected behavior → edge cases → verification`

Preserve unrelated user changes. Prefer isolated branch/worktree when tooling supports it and scope/risk justifies isolation.

Review in two stages:

1. **spec/intent compliance**;
2. **code/experience quality**.

A clean implementation that violates the requested behavior/brand/project truth still fails.

## Verification contract

Every material change should be traceable through:

`change → expected outcome → verification method → pass condition → result`

Important distinctions:

- build pass ≠ visual/functional proof;
- automated accessibility scan ≠ formal conformance;
- one Lighthouse/lab run ≠ field performance outcome;
- deploy job success ≠ post-deploy service health;
- screenshot existence ≠ visual inspection.

## Security/privacy contract

Use risk/trust-boundary reasoning rather than one universal header/regex checklist.

`data/assets/actors → trust boundaries → threats/misuse → controls → verification → residual risk`

Use current authoritative standards/guidance when exact requirements matter. Security/privacy/compliance claims require evidence matching scope and jurisdiction.

## Performance contract

Use key-route/user-condition **performance budgets** instead of universal vanity thresholds.

Budget dimensions can include Core Web Vitals, resource size/count, hero/media/fonts, third parties and runtime work.

Always distinguish lab evidence from field/real-user data.

## Release contract

Production release should know:

- exact change scope;
- verification results/unverified areas;
- P0/P1 blockers/accepted risks;
- env/config/migration/redirect dependencies;
- safe rollback/recovery mechanism;
- post-deploy smoke scope;
- monitoring/learning signals.

Default rollback should be platform previous-deployment rollback or safe revert when appropriate, not destructive force-reset of shared history.

## Evidence contract

Important claims should trace:

`claim → source/evidence → date/context → confidence/limitations → decision → verification/outcome`

Never upgrade an assumption into research evidence.

## Reliability contract

One successful agent run demonstrates capability, not reliability.

Use multiple independent trials when reliability matters, deterministic graders where possible, judgment graders/human calibration where required, and outcome grading over brittle choreography.

## Accessibility contract

Formal accessibility evaluation should use a WCAG-EM-style scoped process: define scope/target, explore product, select representative sample/complete processes, evaluate with appropriate manual/automated/AT methods, and report limitations. Partial review is not a conformance claim.

## Measurement contract

Define success from service purpose/user need before claiming improvement:

`user need → service purpose → outcome → metric → data source → segment/channel → decision threshold → review cadence`

Combine performance data with user research; measure the relevant end-to-end journey when the service continues beyond the website.

## Provider-neutral eval harness

`scripts/eval-harness.py` supports task discovery, result validation and multi-trial summaries. Provider adapters emit the documented JSONL contract so the library remains model/vendor neutral.

## Backward compatibility

- V2/V2.1/V3/V4 profiles remain valid.
- Schema-version-1 and schema-version-2 configs remain valid.
- Existing skill names remain valid.
- V5 uses the existing profile/pack mechanism.

## Research / benchmarking baseline

At execution time verify time-sensitive guidance. V5 is informed by:

- Apple Human Interface Guidelines familiarity/design principles and WWDC26 metaphor guidance;
- Nielsen Norman Group guidance on matching systems to the real world and functional-vs-decorative skeuomorphism;
- Object-Oriented UX (OOUX) mental-model/object-first structure;
- W3C/WAI WCAG-EM evaluation methodology;
- GOV.UK user-needs/service-success/performance-measurement practice;
- OWASP ASVS and relevant Cheat Sheet guidance for web application verification;
- web.dev performance budget and lab/field performance practice;
- public coding-agent skill ecosystems for progressive disclosure, explicit skill routing, verification-before-completion, isolated execution and review patterns;
- project-specific research and evidence, which always takes precedence over generic examples when valid.
