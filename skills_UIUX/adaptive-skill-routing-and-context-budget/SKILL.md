---
name: adaptive-skill-routing-and-context-budget
description: Selects the smallest useful skill graph for the current task based on project context, scope and risk, escalating into UI/UX, product, growth, search, experimentation or engineering specialists only when their decision boundary is active.
---

# Adaptive Skill Routing & Context Budget

## Principle

`maximum decision quality / minimum unnecessary context`

Installed does not mean active. Do not load every skill or external corpus merely because it exists.

## Routing workflow

### 1. Classify task

Scope examples:
- `local` — one component/state/style defect;
- `page` — one page/flow;
- `journey` — multiple steps/pages for an outcome;
- `system/site` — IA/brand/design system/whole-site;
- `production/reliability` — release/conformance/regression/measurement.

Escalate risk for money/privacy/consent/security, accessibility-critical flows, high conversion consequence, major IA/brand change, irreversible migration, complex data/workflow, or weak/conflicting evidence.

### 2. Read project truth first

Project/user/source-of-truth beats generic skill defaults. Load only source sections relevant to the active decision.

### 3. Build the minimal graph

Choose:
- one orchestrator only when needed;
- local/domain owner skills;
- narrow specialists justified by the active decision;
- deeper references only after the specialist is active.

### 4. Escalate when evidence reveals a new risk

Do not pre-load “just in case”. Add a specialist only when the current owner cannot safely resolve a material decision.

### 5. Record material routing

For large work: `task → trigger/risk → skill/packs → material decision → verification`.

## Design / UI external specialists

- `design-intelligence-retrieval` → active UI/product/style/color/type/icon/motion/chart/stack knowledge gap; query smallest relevant domain/system/stack subset.
- `visual-taste-calibration` → after a visual direction exists but remains generic/interchangeable/over-decorated.
- `web-ui-code-review` → source-level UI/pre-merge/root-cause review; React/Next specialization only after stack/version detection.
- `reference-extraction-and-design-audit` → deep extraction from shortlisted references/current system, not every inspiration link.
- `ux-writing-and-microcopy` → string/state copy affects comprehension/action/trust/recovery/localization.

## Cross-functional product/growth specialists

These complement UI/UX; they do not create a second product-management/marketing lifecycle.

- `product-decision-and-stakeholder-framing` → incoming ask is an ambiguous/conflicting solution request and the underlying problem/priority call is unclear.
- `product-strategy-and-prioritization` → problem/outcome is understood enough to position, rank competing opportunities/features or cut scope.
- `conversion-and-content` → marketing-page argument, message match, proof, objections, CTA hierarchy or CRO hypothesis is active.
- `analytics-and-experimentation` → define metrics/counter-metrics, tracking/funnels or a pre-run experiment plan.
- `experimentation-interpretation` → experiment has completed result data and the question is ship/kill/iterate/rerun or why experiment/dashboard numbers disagree.
- `search-demand-and-content-briefing` → current search/query demand or Search Console evidence should influence topic/page role/content brief.
- `seo-strategy` → technical/on-page implementation: indexability/canonical/schema/metadata/sitemap/robots/redirects.
- `ai-agent-coding-guardrails` → coding task needs context curation, dependency-aware plan, vertical slices/checkpoints or change safety.

### Cross-functional ordering examples

```text
Stakeholder says “add chatbot”
→ product-decision-and-stakeholder-framing
→ if a real opportunity survives: product-strategy-and-prioritization
→ then UX/design owners
```

```text
Landing page conversion is low
→ inspect actual evidence
→ conversion-and-content
→ analytics-and-experimentation if testing a hypothesis
→ experimentation-interpretation only after results exist
```

```text
“Create a page for keyword X”
→ search-demand-and-content-briefing if current demand evidence is needed
→ IA/content owners
→ seo-strategy for technical implementation
```

## Progressive disclosure

For any specialist/external knowledge source:

```text
owner/adaptor SKILL.md
→ decide if deeper knowledge is needed
→ one directly linked reference/checklist
→ project evidence
→ act / verify
```

Do not load original upstream repositories during normal project execution simply to restate generic guidance. Source pins are for provenance/update review.

## Precedence and collision control

```text
current user request
→ project truth/source
→ passed Design Contract/artifacts
→ routed local owner skill
→ cross-functional/external specialist synthesis
→ generic model prior
```

Material conflicts are recorded; external PM/growth/SEO conventions cannot silently override project truth, accessibility, security, responsive scope or release authority.

## Near-miss rules

- Header spacing is 2px off a known token → `project-context + ui-improvement`; not product/growth/external specialists.
- CTA label unclear in payment confirmation → `ux-writing-and-microcopy` + system reality if needed; not marketing CRO by default.
- Stakeholder asks for a larger logo and evidence already shows exact brand spec → use project/brand/UI owner; do not run a product-decision workshop.
- Two backlog items lack Reach data → `product-strategy-and-prioritization` may use UNKNOWN/evidence matrix; never fabricate RICE inputs.
- Experiment has not launched → `analytics-and-experimentation`, not `experimentation-interpretation`.
- User asks for meta/canonical bug fix → `seo-strategy`; no live keyword research unless demand is the actual question.
- Single obvious source edit → `ai-agent-coding-guardrails` remains lightweight; no full planning ritual.

## Context budget management

Keep persistent rules/project truth, active contract, current files and current failure evidence. Compress/drop resolved exploration, obsolete tool output and superseded drafts. A larger context window is not permission to flood the task with irrelevant knowledge.

## Gate

If more effort is spent restating frameworks than inspecting the actual project/evidence, reduce the active skill set.

## Anti-patterns

- All packs on every task.
- Product/growth skills activated merely because the project has a business goal.
- CRO best practices reported as proven conversion causes.
- Search volumes or experiment statistics invented to complete a framework.
- Both pre-run and post-run experiment skills loaded when only one lifecycle stage applies.
- External specialist becomes a second orchestrator.
- Deep references loaded before the trigger/decision is known.
